"""用 FFDec 从 SWF 导出脚本、图片和二进制数据。"""
import os
import subprocess

from bqyx_parser.tools.config import save_main_swf_info


class FFDecExporter:
    """FFDec导出器类，用于从SWF文件导出各种资源"""
    # 支持的导出类型
    SUPPORTED_EXPORT_TYPES = {
        'binaryData',
        'font',
        'frame',
        'image',
        'morphshape',
        'movie',
        'script',
        'shape',
        'symbolClass',
        'text'
    }
    ffdec_path = 'ffdec-cli.exe'

    @staticmethod
    def set_ffdec_path(ffdec_path):
        FFDecExporter.ffdec_path = ffdec_path

    def __init__(self,
                 output_dir,
                 input_swf,
                 ):
        """
        初始化FFDec导出器

        Args:
            ffdec_path (str): FFDec可执行文件的路径
            input_swf (Path|str): 输入的SWF文件路径
            output_dir (Path|str): 输出目录路径
        """
        self.input_swf = str(input_swf)
        self.output_dir = str(output_dir)

    def export(self, export_types='all', select_classes=None):
        """
        导出SWF文件中的资源
        export_scripts(['com.example.MyClass', 'com.example.SecondClass'])
        Args:
            export_types (set/list/str): 要导出的资源类型，如果为all则默认导出所有支持的类型
                                       可以是单个类型字符串或类型列表/集合
            select_classes (list, optional): 要导出的AS3类名列表 仅仅用于scripts
        """
        
        # 检查输入文件是否存在
        if not os.path.exists(self.input_swf):
            print(f"输入文件不存在: {self.input_swf}")
            return False

        # 处理导出类型参数
        if export_types is None or export_types == 'all':
            # 默认导出所有支持的类型
            types_to_export = {'all'}
        elif isinstance(export_types, str):
            # 单个类型
            types_to_export = {export_types}
        else:
            # 列表或集合
            types_to_export = set(export_types)
        # 将类型列表转换为逗号分隔的字符串
        export_types_str = ','.join(types_to_export)

        # 构建命令参数
        cmd = [
            self.ffdec_path
        ]
        
        # 如果指定了要导出的类，先添加-selectclass参数
        if select_classes:
            class_str = ','.join(select_classes)
            cmd.extend(["-selectclass", class_str])
            print(f"正在导出 {self.input_swf} 的 {export_types_str} 资源中指定的类到 {self.output_dir}...")
        else:
            print(f"正在导出 {self.input_swf} 的 {export_types_str} 资源到 {self.output_dir}...")
        
        # 添加导出参数
        cmd.extend(["-export", export_types_str, self.output_dir, self.input_swf])
    
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            print("导出完成!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"执行 ffdec-cli.exe 时发生错误: {e}")
            print(f"Return code: {e.returncode}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
        except FileNotFoundError:
            #  不记录版本号
            save_main_swf_info('None')
            raise ValueError(f" {self.ffdec_path}无法运行，ffdec-cli设置错误")
        except Exception as e:
            print(f"发生未预期的错误: {e}")
            return False
    def export_scripts(self, select_classes=None):
        """
        导出脚本资源

        Args:
            select_classes (list, optional): 要导出的AS3类名列表
        """
        return self.export('script', select_classes=select_classes)

    def export_binary_data(self):
        """只导出binaryData资源"""
        return self.export('binaryData')

    def export_images(self):
        """只导出images资源"""
        return self.export('image')

    def export_symbol_class(self):
        """只导出symbolClass资源"""
        return self.export('symbolClass')

    def export_shapes(self):
        """只导出shapes资源"""
        return self.export('shape')

    def export_all(self):
        return self.export(export_types='all')
