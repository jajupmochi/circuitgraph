"""spiceCook.py: Illustration of Exposed Method Calling"""

# Project Imports
from framework.example.spice.spiceGenerator import SpiceGenerator
from framework.example.spice.spiceGeneratorAdvanced import SpiceGeneratorAdvanced
from framework.example.spice.spiceConveyor import SpiceConveyor
from framework.example.spice.spiceRefiner import SpiceRefiner
from framework.utils.Pipeline import Pipeline



bb1 = SpiceGenerator(name="SpiceGenerator")
bb2 = SpiceRefiner(name="SpiceRefiner")
bb3 = SpiceConveyor(name="SpiceConv1")
bb4 = SpiceGeneratorAdvanced(name="SpiceGeneratorAdvanced")

# Direct, Simple Calls
print("---------------")
print(bb1.pepper(amount=666, quality="evil"))
print(bb1.garlic())
print(bb1.salt(amount=50))
print(bb4.garlic())
print(bb4.cinnamon())


# Direct, Consecutive Calls
print("---------------")
garlic = bb1.garlic()
print(garlic)
good_garlic = bb2.selectGarlic(garlicForRefinement=garlic)
print(good_garlic)


# LOCAL Pipeline Config and Calls
print("---------------")
pl = Pipeline()
pl.clear()
step_id_bb1 = pl.add(bb=bb1, method="garlic")
step_id_bb2 = pl.add(bb=bb2, method="selectGarlic", transform={"garlicForRefinement": {"source": step_id_bb1, "slice": None}})
job_id = pl.execute()
print(f"Now i got a job running: {job_id}")
print(f"Can't wait to see its state: {pl.status(job_id)}")
print(f"oh ok, let's wait for it to finish... ")
pl.wait(job_id)
print(f"Wonder what it's state now: {pl.status(job_id)}")
print("Results of Calculation:")
print(pl.result(job_id, step_id_bb1))
print(pl.result(job_id, step_id_bb2))
