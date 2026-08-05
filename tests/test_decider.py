from peano_game.decider import decider
from peano_game.generator import wff


#For the old version of the code,
#write to a file so we can compare to a later version to see if the results are the same
def write_results():
    with open("tests/results.txt", "w") as f:
        for i in range(5000):
            w = wff(i)
            result = decider(w)
            f.write(f"{i}, {result}\n")

def test_compare_results():
    with open("tests/results.txt", "r") as f:
        for i in range(5000):
            line = f.readline()
            assert line.strip() == f"{i}, {decider(wff(i))}"

if __name__ == "__main__":
    write_results()
    test_compare_results()