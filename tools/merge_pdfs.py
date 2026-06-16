#!/usr/bin/env python3
"""Merge individual chapter PDFs into one book using pdfrw."""
import sys
import pdfrw

def merge(input_paths, output_path):
    writer = pdfrw.PdfWriter()
    for path in input_paths:
        try:
            reader = pdfrw.PdfReader(path)
            writer.addpages(reader.pages)
            print(f"  + {path} ({len(reader.pages)} pages)")
        except Exception as e:
            print(f"  ! skip {path}: {e}")
    writer.write(output_path)
    import os
    size = os.path.getsize(output_path)
    print(f"\n  Book PDF: {output_path}")
    print(f"  Size: {size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    merge(sys.argv[1:-1], sys.argv[-1])
