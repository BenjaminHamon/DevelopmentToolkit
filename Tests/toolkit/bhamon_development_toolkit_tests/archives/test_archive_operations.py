# cspell:words fileset

import os
import zipfile

import py
import pytest

from bhamon_development_toolkit.archives.archive_operations import ArchiveOperations
from bhamon_development_toolkit.archives.tar_archive_operations import TarArchiveOperations
from bhamon_development_toolkit.archives.zip_archive_operations import ZipArchiveOperations


def list_implementations():
    return [
        "tar-uncompressed",
        "tar-bz2",
        "tar-gzip",
        "zip-uncompressed",
        "zip-compressed",
    ]


def instantiate_implementation(implementation: str) -> ArchiveOperations:
    if implementation == "tar-uncompressed":
        return TarArchiveOperations(None)

    if implementation == "tar-bz2":
        return TarArchiveOperations("bz2")

    if implementation == "tar-gzip":
        return TarArchiveOperations("gz")

    if implementation == "zip-uncompressed":
        return ZipArchiveOperations(compression = zipfile.ZIP_STORED)

    if implementation == "zip-compressed":
        return ZipArchiveOperations(compression = zipfile.ZIP_DEFLATED)

    raise ValueError("Unsupported implementation '%s'" % implementation)


@pytest.mark.parametrize("implementation", list_implementations())
def test_create(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())

    fileset = [
        (os.path.join(tmpdir, "Source", "Directory_A", "File_A_1"), "Directory_A/File_A_1"),
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
        (os.path.join(tmpdir, "Source", "File_X_2"), "File_X_2"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    operations.create(archive_path, fileset)

    assert os.path.exists(archive_path)


@pytest.mark.parametrize("implementation", list_implementations())
def test_list_files(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())

    fileset = [
        (os.path.join(tmpdir, "Source", "Directory_A", "File_A_1"), "Directory_A/File_A_1"),
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
        (os.path.join(tmpdir, "Source", "File_X_2"), "File_X_2"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    operations.create(archive_path, fileset)

    file_collection = operations.list_files(archive_path)
    assert file_collection == [ dst for _, dst in fileset ]


@pytest.mark.parametrize("implementation", list_implementations())
def test_verify(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())

    fileset = [
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    operations.create(archive_path, fileset)
    operations.verify(archive_path)


@pytest.mark.parametrize("implementation", list_implementations())
def test_verify_corrupted(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())

    fileset = [
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    operations.create(archive_path, fileset)

    with open(archive_path, mode = "rb+") as archive_file:
        archive_file.write(b"0" * 10)

    with pytest.raises(RuntimeError):
        operations.verify(archive_path)


@pytest.mark.parametrize("implementation", list_implementations())
def test_extract(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())

    fileset = [
        (os.path.join(tmpdir, "Source", "Directory_A", "File_A_1"), "Directory_A/File_A_1"),
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
        (os.path.join(tmpdir, "Source", "File_X_2"), "File_X_2"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    operations.create(archive_path, fileset)
    operations.extract(archive_path, os.path.join(tmpdir, "Extraction"))

    for _, destination in fileset:
        assert os.path.exists(os.path.join(tmpdir, "Extraction", os.path.normpath(destination)))


@pytest.mark.parametrize("implementation", list_implementations())
def test_extract_replace(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())
    extra_file_path = os.path.join(tmpdir, "Extraction", "File_Y_1")

    fileset = [
        (os.path.join(tmpdir, "Source", "Directory_A", "File_A_1"), "Directory_A/File_A_1"),
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
        (os.path.join(tmpdir, "Source", "File_X_2"), "File_X_2"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    os.makedirs(os.path.dirname(extra_file_path))
    with open(extra_file_path, mode = "w", encoding = "utf-8"):
        pass

    operations.create(archive_path, fileset)
    operations.extract(archive_path, os.path.join(tmpdir, "Extraction"), replace = True)

    for _, destination in fileset:
        assert os.path.exists(os.path.join(tmpdir, "Extraction", os.path.normpath(destination)))
    assert not os.path.exists(extra_file_path)


@pytest.mark.parametrize("implementation", list_implementations())
def test_extract_keep(tmpdir: py.path.local, implementation: str):
    operations = instantiate_implementation(implementation)

    archive_path = os.path.join(tmpdir, "Archive" + operations.get_file_extension())
    extra_file_path = os.path.join(tmpdir, "Extraction", "File_Y_1")

    fileset = [
        (os.path.join(tmpdir, "Source", "Directory_A", "File_A_1"), "Directory_A/File_A_1"),
        (os.path.join(tmpdir, "Source", "File_X_1"), "File_X_1"),
        (os.path.join(tmpdir, "Source", "File_X_2"), "File_X_2"),
    ]

    for source, _ in fileset:
        os.makedirs(os.path.dirname(source), exist_ok = True)
        with open(source, mode = "w", encoding = "utf-8"):
            pass

    os.makedirs(os.path.dirname(extra_file_path))
    with open(extra_file_path, mode = "w", encoding = "utf-8"):
        pass

    operations.create(archive_path, fileset)
    operations.extract(archive_path, os.path.join(tmpdir, "Extraction"), replace = False)

    for _, destination in fileset:
        assert os.path.exists(os.path.join(tmpdir, "Extraction", os.path.normpath(destination)))
    assert os.path.exists(extra_file_path)
