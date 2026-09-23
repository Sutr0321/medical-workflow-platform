import json
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
src_path = project_root / "src"

sys.path.insert(
    0,
    str(src_path),
)


from medflow.llm.spec_generator import ResearchSpecGenerator


question = """
我想研究成年人中 Vitamin D 水平与高血压之间的关系，
并调整年龄、性别和 BMI。
"""


generator = ResearchSpecGenerator()

candidate = generator.generate(
    question
)


print(
    json.dumps(
        candidate.model_dump(),
        ensure_ascii=False,
        indent=2,
    )
)