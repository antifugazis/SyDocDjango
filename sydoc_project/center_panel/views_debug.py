"""
Debug views for troubleshooting file upload issues.
"""
import os
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

logger = logging.getLogger('center_panel')

class DebugMediaConfigView(View):
    """View to debug media configuration and permissions."""
    
    @method_decorator(login_required)
    def get(self, request):
        """Return media configuration and permissions info."""
        # Check if MEDIA_ROOT exists and is writable
        media_root_exists = os.path.exists(settings.MEDIA_ROOT)
        media_root_writable = os.access(settings.MEDIA_ROOT, os.W_OK) if media_root_exists else False
        
        # Check if upload directories exist and are writable
        upload_dirs = {
            'covers': os.path.join(settings.MEDIA_ROOT, 'books/covers'),
            'digital': os.path.join(settings.MEDIA_ROOT, 'books/digital'),
        }
        
        dir_status = {}
        for name, path in upload_dirs.items():
            exists = os.path.exists(path)
            writable = os.access(path, os.W_OK) if exists else False
            dir_status[name] = {
                'path': path,
                'exists': exists,
                'writable': writable,
                'permissions': oct(os.stat(path).st_mode)[-3:] if exists else None,
            }
        
        # Get file upload handler info
        file_upload_handlers = [
            handler.__module__ + '.' + handler.__name__ 
            for handler in request.upload_handlers
        ]
        
        # Prepare response
        response_data = {
            'media_root': {
                'path': settings.MEDIA_ROOT,
                'exists': media_root_exists,
                'writable': media_root_writable,
                'permissions': oct(os.stat(settings.MEDIA_ROOT).st_mode)[-3:] if media_root_exists else None,
            },
            'media_url': settings.MEDIA_URL,
            'directories': dir_status,
            'file_upload_handlers': file_upload_handlers,
            'debug': settings.DEBUG,
            'file_upload_max_memory_size': getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 2621440),  # Default 2.5MB
            'data_upload_max_memory_size': getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 2621440),  # Default 2.5MB
        }
        
        logger.info("Media configuration debug info", extra={'data': response_data})
        return JsonResponse(response_data)


def debug_upload(request):
    """Debug view to test file uploads."""
    if request.method == 'POST' and request.FILES:
        file = request.FILES['file']
        
        # Log file info
        file_info = {
            'name': file.name,
            'size': file.size,
            'content_type': file.content_type,
            'charset': getattr(file, 'charset', None),
            'content_type_extra': getattr(file, 'content_type_extra', {}),
        }
        logger.info("File upload received", extra={'file_info': file_info})
        
        # Save the file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            
            temp_path = temp_file.name
            file_size = os.path.getsize(temp_path)
            
            logger.info(f"File saved temporarily to {temp_path} ({file_size} bytes)")
            
            # Clean up
            try:
                os.unlink(temp_path)
                logger.info("Temporary file cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {str(e)}")
        
        return JsonResponse({
            'status': 'success',
            'file_info': file_info,
            'temp_path': temp_path,
            'file_size': file_size,
        })
    
    return JsonResponse({'status': 'error', 'message': 'No file provided'}, status=400)
