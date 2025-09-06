import hashlib
import os
import re
import subprocess
import zipfile
from datetime import datetime
from typing import Dict, List, Tuple, Any

from phase1.models.database import File, Class, Method


class JarParser:
    """Parser to extract class and method signatures from JAR files."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        try:
            from phase1.utils.logger import LoggerFactory
            self.logger = LoggerFactory.get_parser_logger("jar")
        except Exception:
            self.logger = None

    def can_parse(self, file_path: str) -> bool:
        return file_path.endswith('.jar')

    def parse_file(self, jar_path: str, project_id: int) -> Tuple[File, List[Class], List[Method], List]:
        """Parse the JAR file and extract classes and method signatures."""
        with open(jar_path, 'rb') as f:
            jar_bytes = f.read()
        file_hash = hashlib.sha256(jar_bytes).hexdigest()
        file_stat = os.stat(jar_path)
        file_obj = File(
            project_id=project_id,
            path=jar_path,
            language='jar',
            hash=file_hash,
            loc=0,
            mtime=datetime.fromtimestamp(file_stat.st_mtime)
        )

        classes: List[Class] = []
        methods: List[Method] = []

        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                class_entries = [c for c in jar.namelist() if c.endswith('.class')]
        except zipfile.BadZipFile:
            if self.logger:
                self.logger.warning(f"잘못된 JAR 파일: {jar_path}")
            return file_obj, classes, methods, []

        for entry in class_entries:
            class_name = entry[:-6].replace('/', '.')
            cls = Class(file_id=None, fqn=class_name, name=class_name.split('.')[-1])
            classes.append(cls)
            try:
                result = subprocess.run(
                    ['javap', '-p', '-classpath', jar_path, class_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                output = result.stdout
                for line in output.splitlines():
                    line = line.strip()
                    if '(' not in line or ';' not in line:
                        continue
                    m = re.match(r'^.*?([\w\[\]<>$]+)\s+(\w+)\(([^)]*)\);', line)
                    if not m:
                        continue
                    return_type, name, params = m.groups()
                    signature = f"{return_type} {name}({params})".strip()
                    method_obj = Method(
                        class_id=None,
                        name=name,
                        signature=signature,
                        return_type=return_type,
                        parameters=params
                    )
                    method_obj.owner_fqn = class_name
                    methods.append(method_obj)
            except FileNotFoundError:
                if self.logger:
                    self.logger.warning('javap 명령을 찾을 수 없습니다. 메서드 추출을 건너뜁니다.')
                break

        return file_obj, classes, methods, []