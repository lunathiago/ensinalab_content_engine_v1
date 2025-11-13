"""
Abstração de Storage para vídeos
Suporta: Cloudflare R2, AWS S3, Local Filesystem
"""
import os
import boto3
import unicodedata
from pathlib import Path
from typing import Optional, Dict
from botocore.exceptions import ClientError


class VideoStorage:
    """
    Gerenciador de storage para vídeos
    
    Prioridade:
    1. Cloudflare R2 (se R2_ACCESS_KEY_ID configurado)
    2. AWS S3 (se AWS_S3_BUCKET_NAME configurado)
    3. Local filesystem (fallback para desenvolvimento)
    """
    
    def __init__(self):
        self.use_r2 = bool(os.getenv("R2_ACCESS_KEY_ID"))
        self.use_s3 = bool(os.getenv("AWS_S3_BUCKET_NAME")) and not self.use_r2
        self.use_local = not (self.use_r2 or self.use_s3)
        
        if self.use_r2:
            self._init_r2()
        elif self.use_s3:
            self._init_s3()
        
        print(f"📦 Storage configurado: {'R2' if self.use_r2 else 'S3' if self.use_s3 else 'Local'}")
    
    def _init_r2(self):
        """Inicializa cliente Cloudflare R2"""
        account_id = os.getenv("R2_ACCOUNT_ID")
        endpoint_url = os.getenv("R2_ENDPOINT_URL") or f"https://{account_id}.r2.cloudflarestorage.com"
        
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
            region_name='auto'  # R2 usa 'auto'
        )
        
        self.bucket = os.getenv("R2_BUCKET_NAME", "ensinalab-videos")
        self.public_url = os.getenv("R2_PUBLIC_URL")  # Opcional: custom domain
        
        print(f"   ✓ R2 Bucket: {self.bucket}")
        if self.public_url:
            print(f"   ✓ Public URL: {self.public_url}")
    
    def _init_s3(self):
        """Inicializa cliente AWS S3"""
        self.client = boto3.client(
            's3',
            region_name=os.getenv("AWS_S3_REGION", "us-east-1")
        )
        
        self.bucket = os.getenv("AWS_S3_BUCKET_NAME")
        self.public_url = None  # S3 usa presigned URLs
        
        print(f"   ✓ S3 Bucket: {self.bucket}")
    
    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """
        Remove caracteres não-ASCII dos metadados S3/R2
        
        S3/R2 metadata só aceita ASCII. Remove acentos e caracteres especiais.
        
        Args:
            metadata: Dicionário com metadados originais
        
        Returns:
            Dicionário com valores sanitizados (apenas ASCII)
        """
        sanitized = {}
        
        for key, value in metadata.items():
            # Converter valor para string
            str_value = str(value)
            
            # Normalizar Unicode (NFD = Normalization Form Decomposed)
            # Exemplo: "á" vira "a" + "´" (acento separado)
            nfd = unicodedata.normalize('NFD', str_value)
            
            # Remover marcas diacríticas (acentos, til, cedilha)
            ascii_value = ''.join(
                char for char in nfd 
                if unicodedata.category(char) != 'Mn'  # Mn = Nonspacing Mark
            )
            
            # Garantir apenas ASCII (remover qualquer caractere > 127)
            ascii_value = ascii_value.encode('ascii', 'ignore').decode('ascii')
            
            sanitized[key] = ascii_value
        
        return sanitized
    
    def upload_video(
        self, 
        local_path: str, 
        video_id: int,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Faz upload do vídeo para storage
        
        Args:
            local_path: Caminho local do arquivo
            video_id: ID do vídeo
            metadata: Metadata adicional (título, duração, etc)
        
        Returns:
            URL pública do vídeo ou caminho local
        """
        
        if self.use_local:
            # Desenvolvimento: manter arquivo local
            return local_path
        
        try:
            # Key único para o vídeo
            key = f"videos/video_{video_id}.mp4"
            
            # Preparar metadata para S3/R2
            extra_args = {
                'ContentType': 'video/mp4',
                'CacheControl': 'max-age=31536000',  # 1 ano
            }
            
            if metadata:
                # Sanitizar metadados (S3 só aceita ASCII)
                sanitized = self._sanitize_metadata(metadata)
                extra_args['Metadata'] = sanitized
                
                # Log se houve mudanças
                if any(sanitized[k] != str(metadata[k]) for k in metadata.keys()):
                    print(f"   ⚠️  Metadados sanitizados (acentos removidos)")
            
            # Upload
            print(f"   📤 Uploading para {self.bucket}/{key}...")
            
            self.client.upload_file(
                local_path,
                self.bucket,
                key,
                ExtraArgs=extra_args
            )
            
            # Retornar URL
            if self.use_r2 and self.public_url:
                # R2 com custom domain
                url = f"{self.public_url}/{key}"
            elif self.use_r2:
                # R2 com URL padrão
                account_id = os.getenv("R2_ACCOUNT_ID")
                url = f"https://pub-{account_id}.r2.dev/{key}"
            else:
                # S3 - gerar presigned URL (24h)
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket, 'Key': key},
                    ExpiresIn=86400
                )
            
            print(f"   ✅ Upload concluído: {url[:60]}...")
            
            # Deletar arquivo local após upload (economizar espaço)
            try:
                os.remove(local_path)
                print(f"   🗑️  Arquivo local deletado: {local_path}")
            except:
                pass
            
            return url
            
        except ClientError as e:
            error_msg = str(e)
            print(f"   ❌ Erro no upload: {error_msg}")
            
            # Se erro de validação de metadados, tentar novamente SEM metadata
            if "Parameter validation failed" in error_msg or "Non ascii" in error_msg:
                print(f"   🔄 Tentando novamente sem metadados...")
                try:
                    self.client.upload_file(
                        local_path,
                        self.bucket,
                        key,
                        ExtraArgs={
                            'ContentType': 'video/mp4',
                            'CacheControl': 'max-age=31536000'
                        }
                    )
                    
                    # Gerar URL normalmente
                    if self.use_r2 and self.public_url:
                        url = f"{self.public_url}/{key}"
                    elif self.use_r2:
                        account_id = os.getenv("R2_ACCOUNT_ID")
                        url = f"https://pub-{account_id}.r2.dev/{key}"
                    else:
                        url = self.client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': self.bucket, 'Key': key},
                            ExpiresIn=86400
                        )
                    
                    print(f"   ✅ Upload concluído (sem metadata): {url[:60]}...")
                    
                    # Deletar arquivo local
                    try:
                        os.remove(local_path)
                        print(f"   🗑️  Arquivo local deletado: {local_path}")
                    except:
                        pass
                    
                    return url
                    
                except Exception as retry_error:
                    print(f"   ❌ Retry falhou: {retry_error}")
            
            # Fallback: retornar path local
            return local_path
        except Exception as e:
            print(f"   ❌ Erro inesperado: {e}")
            return local_path
    
    def upload_thumbnail(
        self, 
        local_path: str, 
        video_id: int
    ) -> str:
        """
        Faz upload da thumbnail
        
        Returns:
            URL pública da thumbnail
        """
        
        if self.use_local:
            return local_path
        
        try:
            key = f"thumbnails/video_{video_id}.jpg"
            
            self.client.upload_file(
                local_path,
                self.bucket,
                key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                    'CacheControl': 'max-age=31536000'
                }
            )
            
            if self.use_r2 and self.public_url:
                url = f"{self.public_url}/{key}"
            elif self.use_r2:
                account_id = os.getenv("R2_ACCOUNT_ID")
                url = f"https://pub-{account_id}.r2.dev/{key}"
            else:
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket, 'Key': key},
                    ExpiresIn=86400
                )
            
            # Deletar local
            try:
                os.remove(local_path)
            except:
                pass
            
            return url
            
        except Exception as e:
            print(f"   ⚠️ Erro no upload de thumbnail: {e}")
            return local_path
    
    def delete_video(self, video_id: int) -> bool:
        """
        Remove vídeo do storage
        
        Returns:
            True se deletado com sucesso
        """
        
        if self.use_local:
            return False  # Não deletar localmente em dev
        
        try:
            key = f"videos/video_{video_id}.mp4"
            
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            
            print(f"   🗑️  Vídeo deletado: {key}")
            return True
            
        except Exception as e:
            print(f"   ⚠️ Erro ao deletar: {e}")
            return False
    
    def delete_thumbnail(self, video_id: int) -> bool:
        """Remove thumbnail do storage"""
        
        if self.use_local:
            return False
        
        try:
            key = f"thumbnails/video_{video_id}.jpg"
            
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            
            return True
            
        except Exception as e:
            print(f"   ⚠️ Erro ao deletar thumbnail: {e}")
            return False
    
    def get_video_url(self, video_id: int, expires_in: int = 86400) -> Optional[str]:
        """
        Gera URL de acesso ao vídeo
        
        Args:
            video_id: ID do vídeo
            expires_in: Tempo de expiração em segundos (padrão 24h)
        
        Returns:
            URL de acesso ou None se não encontrado
        """
        
        if self.use_local:
            return f"generated_videos/video_{video_id}_simple.mp4"
        
        try:
            key = f"videos/video_{video_id}.mp4"
            
            if self.use_r2 and self.public_url:
                # URL pública permanente
                return f"{self.public_url}/{key}"
            elif self.use_r2:
                # R2 sem custom domain - gerar presigned URL
                account_id = os.getenv("R2_ACCOUNT_ID")
                return f"https://pub-{account_id}.r2.dev/{key}"
            else:
                # S3 - presigned URL temporária
                return self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket, 'Key': key},
                    ExpiresIn=expires_in
                )
                
        except Exception as e:
            print(f"   ⚠️ Erro ao gerar URL: {e}")
            return None
    
    def check_bucket_exists(self) -> bool:
        """
        Verifica se o bucket existe e está acessível
        
        Returns:
            True se bucket está OK
        """
        
        if self.use_local:
            return True
        
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return True
        except ClientError:
            return False


# Singleton global
_storage_instance: Optional[VideoStorage] = None


def get_storage() -> VideoStorage:
    """
    Retorna instância singleton do storage
    
    Usage:
        storage = get_storage()
        url = storage.upload_video(local_path, video_id)
    """
    global _storage_instance
    
    if _storage_instance is None:
        _storage_instance = VideoStorage()
    
    return _storage_instance
