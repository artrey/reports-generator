import secrets
import difflib as df

import typing
from os.path import basename

from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML

from report.models import Report, Task, SourceFile

ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ'
ALPHABET = ALPHABET + ALPHABET.lower() + 'L' + '23456789'


def build_pdf(html: str, **kwargs):
    return HTML(string=html, **kwargs).render().write_pdf()


def build_pdf_by_template(template: str, context: dict, **kwargs):
    return build_pdf(render_to_string(template, context=context), **kwargs)


def build_report_pdf(report: Report, **kwargs):
    return build_pdf_by_template('report/pdf_report_template.html', {'report': report}, **kwargs)


def build_task_pdf(task: Task, **kwargs):
    return build_pdf_by_template('report/pdf_task_template.html', {'task': task}, **kwargs)


def gen_pass(length: int = 14) -> str:
    password = ''.join(secrets.choice(ALPHABET) for _ in range(length))
    return password


def match_files_by_ratio(src: Report, dst: Report) -> (list, dict, dict):
    files_names = {}
    files_contents = {}
    ratio_pairs = []

    for f1 in src.source_files.all():  # type: SourceFile
        f1_content = files_contents.setdefault(f1.id, f1.file.read())
        f1_name = files_names.setdefault(f1.id, basename(f1.file.name))

        for f2 in dst.source_files.all():  # type: SourceFile
            f2_content = files_contents.setdefault(f2.id, f2.file.read())
            f2_name = files_names.setdefault(f2.id, basename(f2.file.name))

            ratio = df.SequenceMatcher(None, f1_content, f2_content).ratio()

            is_same_names = f1_name == f2_name  # TODO: make with distance

            ratio_pairs.append((is_same_names, ratio, f1.id, f2.id))

            if is_same_names:
                break

    ratio_pairs.sort(reverse=True)

    matched_files = []
    while ratio_pairs:
        _, ratio, left, right = ratio_pairs.pop(0)
        matched_files.append((ratio, left, right))
        ratio_pairs = list(filter(lambda x: x[2] != left and x[3] != right, ratio_pairs))

    return matched_files, files_names, files_contents


def ratio_reports(src: Report, dst: Report) -> float:
    matched_files, _, files_contents = match_files_by_ratio(src, dst)

    ratios = sum((ratio * len(files_contents[fid1]) for ratio, fid1, _ in matched_files))
    return ratios / sum((len(files_contents[fid1]) for _, fid1, _ in matched_files))


def compare_reports(src: Report, dst: Report) -> typing.List[typing.Tuple[float, str]]:
    matched_files, files_names, files_contents = match_files_by_ratio(src, dst)

    return [
        (ratio, df.HtmlDiff(tabsize=4).make_file(
            files_contents[fid1].decode().splitlines(),
            files_contents[fid2].decode().splitlines(),
            files_names[fid1], files_names[fid2]
        ))
        for ratio, fid1, fid2 in matched_files
    ]


def is_valid_filename_ext(extension: str) -> bool:
    if not extension:
        return False
    if extension.lower() in settings.BLACKLIST_FILE_EXTENSIONS:
        return False
    return True
