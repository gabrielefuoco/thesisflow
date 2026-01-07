from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules in 'src'
hiddenimports = collect_submodules('src')

# Optional: collect data files if any
datas = collect_data_files('src')
