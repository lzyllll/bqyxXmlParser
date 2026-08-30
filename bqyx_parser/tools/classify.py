"""按 father 的 name/type 把 XML 分类到 output 目录。"""
from enum import Enum
from pathlib import Path
import shutil

from lxml import etree

from bqyx_parser.parser import Element, load_xml


class FatherStatus(Enum):
    """father 上 name/type 的组合。"""
    BOTH_HAS = "both_has"
    HAS_NAME = "has_name"
    HAS_TYPE = "has_type"
    NO_ATTR = "no_attr"


def get_xml_root(input_file) -> Element:
    return load_xml(input_file, strip_cdata=False)


def check_father_status(father: Element) -> FatherStatus:
    name = father.attrib.get("name")
    type_name = father.attrib.get("type")
    if name is not None and type_name is not None:
        return FatherStatus.BOTH_HAS
    if name is not None:
        return FatherStatus.HAS_NAME
    if type_name is not None:
        return FatherStatus.HAS_TYPE
    return FatherStatus.NO_ATTR


def get_first_child(element: Element):
    return element.find("*")


def has_father(element: Element) -> bool:
    first_child = get_first_child(element)
    return first_child is not None and first_child.tag == "father"


def save_child_elements_to_xml(child_elements, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not child_elements:
        return

    new_root = etree.Element("data")
    for element in child_elements:
        new_root.append(element)

    xml_str = etree.tostring(
        new_root,
        encoding="utf-8",
        pretty_print=True,
        xml_declaration=True,
    ).decode("utf-8")
    output_path.write_text(xml_str, encoding="utf-8")


def ensure_dict_path(dic, keys, default_factory=list):
    current = dic
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    if keys[-1] not in current:
        current[keys[-1]] = default_factory() if callable(default_factory) else default_factory
    return current[keys[-1]]


def generate_xml_files(dic, base_output_dir):
    base_dir = Path(base_output_dir)
    for first_child_tag, status_dict in dic.get("father", {}).items():
        for name_value, child_elements in status_dict.get("name", {}).items():
            output_path = base_dir / "father" / first_child_tag / "name" / f"{name_value}.xml"
            save_child_elements_to_xml(child_elements, output_path)

        for type_value, child_elements in status_dict.get("type", {}).items():
            output_path = base_dir / "father" / first_child_tag / "type" / f"{type_value}.xml"
            save_child_elements_to_xml(child_elements, output_path)

        if "both" in status_dict:
            save_child_elements_to_xml(
                status_dict["both"],
                base_dir / "father" / first_child_tag / "both.xml",
            )

        if "no" in status_dict:
            save_child_elements_to_xml(
                status_dict["no"],
                base_dir / "father" / first_child_tag / "no.xml",
            )


def classify_xml(xml_dir: Path, output_dir: Path):
    """把 xml_dir 中的文件拆到 output_dir/father 和 other。"""
    dic = {}
    for xml_file in xml_dir.iterdir():
        root = get_xml_root(xml_file)
        if has_father(root):
            for father in root.findall("father"):
                father_status = check_father_status(father)
                for child in father.findall("*"):
                    child_tag = child.tag
                    if father_status == FatherStatus.HAS_NAME:
                        target_list = ensure_dict_path(
                            dic, ["father", child_tag, "name", father.get("name")], list
                        )
                    elif father_status == FatherStatus.HAS_TYPE:
                        target_list = ensure_dict_path(
                            dic, ["father", child_tag, "type", father.get("type")], list
                        )
                    elif father_status == FatherStatus.BOTH_HAS:
                        target_list = ensure_dict_path(
                            dic, ["father", child_tag, "name", father.get("name")], list
                        )
                    else:
                        target_list = ensure_dict_path(dic, ["father", child_tag, "no"], list)
                    target_list.append(child)
        else:
            other_dir = Path(output_dir) / "other"
            other_dir.mkdir(exist_ok=True, parents=True)
            shutil.copy2(xml_file, other_dir / xml_file.name)
    generate_xml_files(dic, output_dir)
