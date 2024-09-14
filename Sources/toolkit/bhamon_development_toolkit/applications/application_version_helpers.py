from typing import List, Optional, Tuple


def convert_version_to_numeric_tuple(version_identifier: str, expected_size: Optional[int] = None) -> Tuple[int,...]:
    version_number_list: List[int] = []

    for version_element in version_identifier.split("."):
        try:
            version_element_as_number = int(version_element)
        except ValueError as exception:
            raise ValueError("Version identifier must be numbers only (VersionIdentifier: '%s')" % version_identifier) from exception
        version_number_list.append(version_element_as_number)

    if expected_size is not None:
        if len(version_number_list) > expected_size:
            raise ValueError("Version identifier must have at most %s numbers (VersionIdentifier: '%s')" % (expected_size, version_identifier))
        if len(version_number_list) < expected_size:
            version_number_list += [ 0 ] * (expected_size - len(version_number_list))

    return tuple(version_number_list)
