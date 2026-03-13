import os
import shutil

for f in os.listdir("pipeline"):
    shutil.copy(f, "../CopperMT/pipeline")

for f in os.listdir("neural_translation"):
    shutil.copy(f, "../CopperMT/pipeline/neural_translation")

for f in os.listdir("statistical_translation"):
    shutil.copy(f, "../CopperMT/pipeline/statistical_translation")
    