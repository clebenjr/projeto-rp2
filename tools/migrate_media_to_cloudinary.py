#!/usr/bin/env python3
"""Migrate local MEDIA files into Django's default storage.

Usage:
  - Ensure `DJANGO_SETTINGS_MODULE` is set (e.g. `projetoRP2.settings`) and
    `CLOUDINARY_URL` is set in the environment to point to Cloudinary.
  - Run: `python3 tools/migrate_media_to_cloudinary.py [--dry-run]`

Behavior:
  - Iterates `Vendedor.foto_perfil`, `Produto.imagem`, and `ImagemProduto.imagem`.
  - For each file present on disk under `settings.MEDIA_ROOT`, opens it and
    saves it through `default_storage.save(...)`. When Cloudinary is configured
    as the default storage, the file will be uploaded to Cloudinary.
  - Updates model fields to point to the saved name returned by storage.
  - Supports `--dry-run` to list actions without performing uploads/changes.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Don't perform uploads or DB writes")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of objects processed per batch (no effect currently)")
    args = parser.parse_args()

    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        print("Error: set DJANGO_SETTINGS_MODULE (for example 'projetoRP2.settings') before running.")
        sys.exit(2)

    import django
    django.setup()

    from django.conf import settings
    from django.core.files import File
    from django.core.files.storage import default_storage

    try:
        from appWeb.models import Vendedor, Produto, ImagemProduto
    except Exception as e:
        print("Error importing models:", e)
        sys.exit(1)

    media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
    print(f"MEDIA_ROOT = {media_root}")
    print("Dry run:" , args.dry_run)

    def migrate_field(queryset, field_name, model_name):
        total = queryset.count()
        print(f"Processing {total} {model_name} objects for field '{field_name}'")
        i = 0
        for inst in queryset.iterator():
            i += 1
            file_field = getattr(inst, field_name)
            if not file_field:
                continue
            name = file_field.name
            src = media_root / name
            if not src.exists():
                print(f"  [{i}/{total}] SKIP missing file for {model_name}.{field_name}: {src}")
                continue
            print(f"  [{i}/{total}] Found file: {src}")
            if args.dry_run:
                continue
            # open and save via default_storage
            try:
                with open(src, "rb") as f:
                    django_file = File(f)
                    saved_name = default_storage.save(name, django_file)
                # update model field to saved_name
                setattr(inst, field_name, saved_name)
                inst.save(update_fields=[field_name])
                print(f"    Uploaded -> {saved_name}")
            except Exception as e:
                print(f"    ERROR uploading {src}: {e}")

    # 1) Vendedor.foto_perfil
    migrate_field(Vendedor.objects.all(), "foto_perfil", "Vendedor")

    # 2) Produto.imagem
    migrate_field(Produto.objects.all(), "imagem", "Produto")

    # 3) ImagemProduto.imagem
    migrate_field(ImagemProduto.objects.all(), "imagem", "ImagemProduto")

    print("Done. If not dry-run, files should now be stored via default_storage.")

if __name__ == "__main__":
    main()
