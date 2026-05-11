import os
import shutil

for f in os.listdir("root"):
    f = os.path.join("root", f)
    shutil.copy(f, "../CopperMT")

for f in os.listdir("pipeline"):
    f = os.path.join("pipeline", f)
    shutil.copy(f, "../CopperMT/pipeline")

for f in os.listdir("neural_translation"):
    f = os.path.join("neural_translation", f)
    shutil.copy(f, "../CopperMT/pipeline/neural_translation")

for f in os.listdir("statistical_translation"):
    f = os.path.join("statistical_translation", f)
    shutil.copy(f, "../CopperMT/pipeline/statistical_translation")
    