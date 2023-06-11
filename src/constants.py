from pathlib import Path


server_folder = (Path(__file__).parent / "server").absolute()
favicon = server_folder / "static" / "favicon.ico"
avatar_folder = server_folder / "db" / "avatars"
default_avatar = avatar_folder / "unknown_user.png"
pdfs_folder = server_folder / "db" / "pdfs"
