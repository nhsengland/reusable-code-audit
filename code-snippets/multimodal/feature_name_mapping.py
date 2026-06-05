"""Source: P61/P81 MM-HealthFair — https://github.com/nhsengland/mm-healthfair (src/utils/shap_utils.py)"""


def get_feature_names(test_set, modalities):
    fn_map = {}
    for modality_type in modalities:
        if modality_type == "static":
            fn_map["static"] = test_set.get_feature_list()
        elif modality_type == "timeseries":
            fn_map["ts-vitals"] = test_set.get_feature_list("dynamic0")
            fn_map["ts-labs"] = test_set.get_feature_list("dynamic1")
    return fn_map
