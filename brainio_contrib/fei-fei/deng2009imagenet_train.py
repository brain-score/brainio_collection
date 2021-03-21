import logging
import numpy as np
import os
import sys
from pathlib import Path
from tqdm import tqdm

from brainio_base.stimuli import StimulusSet
from brainio_collection.lookup import sha1_hash
from brainio_collection.packaging import create_image_csv, upload_to_s3


def collect_stimuli(stimuli_dir):
    files = stimuli_dir.glob('*/*')
    stimulus_set = []
    for file in tqdm(files, desc='files', total=1_281_167):
        synset = file.parent.name
        stimulus_set.append({
            'synset': synset,
            'image_id': file.name,
            'filename': file.name,
            'filepath': file,
            'relative_path': file.parent.name + '/'  + file.name,
            'sha1': sha1_hash(file),
        })
    stimulus_set = StimulusSet(stimulus_set)
    stimulus_set.image_paths = {row.image_id: row.filepath for row in stimulus_set.itertuples()}
    stimulus_set['split'] = 'train'
    stimulus_set['image_path_within_store'] = stimulus_set['filename'].apply(
        lambda filename: os.path.splitext(filename)[0])
    assert len(stimulus_set) == 1_281_167
    assert len(np.unique(stimulus_set['image_id'])) == len(stimulus_set), "duplicate image_ids"
    assert len(np.unique(stimulus_set['sha1'])) == 1_275_232  # lots of duplicates apparently
    assert len(np.unique(stimulus_set['synset'])) == 1_000
    del stimulus_set['filepath']
    return stimulus_set


def main():
    stimuli_dir = Path('/braintree/data2/active/common/imagenet_raw/train')
    assert stimuli_dir.is_dir()

    stimuli = collect_stimuli(stimuli_dir)
    identifier = 'fei-fei.Deng2009.train'

    # Only package the csv, not the image zip. The full training set is 140G so we do not want to store on
    # or retrieve from S3. Instead, we store the csv with metadata on S3 and then use locally stored image files.
    # We use excerpts from
    # https://github.com/brain-score/brainio_collection/blob/992ae550d38681843cabfc37509d540acc44c8f6/brainio_collection/packaging.py#L141-L161
    # to package the csv (and not the image zip).
    print('Packaging csv')
    bucket_name = 'brainio.contrib'
    image_store_identifier = "image_" + identifier.replace(".", "_")
    csv_file_name = image_store_identifier + ".csv"
    target_csv_path = Path(__file__).parent / csv_file_name
    csv_sha1 = create_image_csv(stimuli, str(target_csv_path))
    print(f"CSV sha1: {csv_sha1}")
    upload_to_s3(str(target_csv_path), bucket_name, target_s3_key=csv_file_name)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    for logger_ignore in ['urllib3', 'botocore', 'boto3', 's3transfer']:
        logging.getLogger(logger_ignore).setLevel(logging.INFO)
    main()
