from data_owner.models.dataset import Dataset
from data_owner.services.data_base import Database

data_base = Database({'DB_ENGINE': 'sqlite:///data_owner.db'})

datasets = [
    Dataset(1, "file1", ["feature1", "feature2"], 1, 50, 2, 10),
    Dataset(2, "file2", ["feature3", "feature4"], 2, 25, 1, 5),
    Dataset(3, "file3", ["feature5", "feature6"], 3, 30, 5, 15),
    Dataset(4, "file4", ["feature1", "feature2"], 1, 50, 2, 10)
]

datasets_str = [str(dataset) for dataset in datasets]
[dataset.save() for dataset in datasets]


def test_find_dataset2_by_ext_id():
    result = Dataset.find_one_by_external_id(2)
    expected = datasets_str[1]
    assert(str(result) == str(expected))


def test_find_by_all_features():
    features_filter = ["feature1", "feature2"]
    result = [str(res) for res in Dataset.find_one_by_features(features_filter, all=True)]
    expected = [datasets_str[0], datasets_str[3]]
    for i in range(len(result)):
        assert(result[i] == expected[i])


def test_find_all_datasets():
    result = [str(res) for res in Dataset.find_all()]
    expected = datasets_str
    for i in range(len(result)):
        assert(result[i] == expected[i])


test_find_dataset2_by_ext_id()
test_find_by_all_features()
test_find_all_datasets()
