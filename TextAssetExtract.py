import os
import sys
from UnityPy import AssetsManager
from collections import Counter
import zipfile

TYPES = ['TextAsset']

ROOT = os.path.dirname(os.path.realpath(__file__))

# source folder
ASSETS = os.path.abspath(sys.argv[1])
# destination folder
DST = os.path.abspath(sys.argv[2])
# number of dirs to ignore
# e.g. IGNOR_DIR_COUNT = 2 will reduce
# 'assets/assetbundles/images/story_picture/small/15.png'
# to
# 'images/story_picture/small/15.png'

IGNOR_DIR_COUNT = 2

os.makedirs(DST, exist_ok=True)

def main():
	print("AssetBundle path : " + ASSETS)
	print("Destination path : " + DST)
	for root, dirs, files in os.walk(ASSETS, topdown=False):
		if '.git' in root:
			continue
		for f in files:
			print("Extracting : " + f)
			extension = os.path.splitext(f)[1]
			src = os.path.realpath(os.path.join(root, f))

			if extension == ".zip":
				archive = zipfile.ZipFile(src, 'r')
				for zf in archive.namelist():
					extract_assets(archive.open(zf))
			else:
				extract_assets(src)
		print("Extraction completed.")


def extract_assets(src):
	# load source
	am = AssetsManager(src)

	# iterate over assets
	for asset in am.assets.values():
		# assets without container / internal path will be ignored for now
		if not asset.container:
			continue

		# check which mode we will have to use
		num_cont = sum(1 for obj in asset.container.values() if obj.type in TYPES)
		num_objs = sum(1 for obj in asset.objects.values() if obj.type in TYPES)

		# check if container contains all important assets, if yes, just ignore the container
		if num_objs <= num_cont * 2:
			for asset_path, obj in asset.container.items():
				fp = os.path.join(DST, *asset_path.split('/')[IGNOR_DIR_COUNT:])
				export_obj(obj, fp)

		# otherwise use the container to generate a path for the normal objects
		else:
			extracted = []
			# find the most common path
			occurence_count = Counter(os.path.splitext(asset_path)[0] for asset_path in asset.container.keys())
			local_path = os.path.join(DST, *occurence_count.most_common(1)[0][0].split('/')[IGNOR_DIR_COUNT:])

			for obj in asset.objects.values():
				if obj.path_id not in extracted:
					extracted.extend(export_obj(obj, local_path, append_name=True))


def export_obj(obj, fp: str, append_name: bool = False) -> list:
	if obj.type not in TYPES:
		return []
	data = obj.read()
	if append_name:
		fp = os.path.join(fp, data.name)

	fp, extension = os.path.splitext(fp)
	os.makedirs(os.path.dirname(fp), exist_ok=True)

	if obj.type == 'TextAsset':
		if not extension:
			extension = '.txt'
		with open(f"{fp}{extension}", 'wb') as f:
			f.write(data.script)

	return [obj.path_id]


if __name__ == '__main__':
	main()
