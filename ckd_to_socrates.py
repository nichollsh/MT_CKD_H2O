import numpy as np
import sys, os
from netCDF4 import Dataset
import matplotlib.pyplot as plt

def main(in_file:str, out_file:str):

    # Read file
    ds = Dataset(in_file)
    nu = ds.variables["wavenumbers"][:]
    ab = ds.variables["self_absorption"][:]
    ds.close()

    # Convert units
    nu = np.array(nu)
    ab = np.array(ab) * 1.0e20

    # Stats
    numin = nu[0]
    numax = nu[-1]
    dnu   = nu[1]-nu[0]
    nvals = len(nu)

    # Output path
    out_file = out_file.strip()
    if out_file in ["", "."]:
        raise Exception("Output file path is invalid")
    out_file = os.path.abspath(out_file)
    if os.path.exists(out_file):
        os.remove(out_file)

    # Write file
    with open(out_file, 'w') as hdl:
        
        # Header
        hdl.write("*BEGIN_DATA \n\n")
        hdl.write("     Start of table                =  %.6e     cm-1 \n"%numin)
        hdl.write("     End of table                  =  %.6e     cm-1 \n"%numax)
        hdl.write("     Increment in table            =  %.6e     cm-1 \n"%dnu)
        hdl.write("     Number of points in table     =  %d \n\n"%nvals)
        hdl.write("     Continuum coefficients (cm^3.molec-1 * 1.0E-20) \n")

        # Body
        arr_as_str = ""
        for i in range(nvals):
            arr_as_str += "    %.5e"%ab[i]
            if (i+1)%4 == 0:
                arr_as_str += " \n"
        if arr_as_str[-1] != "\n":
            arr_as_str += "\n"
        hdl.write(arr_as_str)

        # Footer
        hdl.write("*END\n")

    # Make plot
    fig,ax = plt.subplots()
    ax.plot(nu, ab)
    ax.set_xlabel("Wavenumber (cm-1)")
    ax.set_ylabel("Self-absorption (cm^3.molec-1 * 1.0E-20)")
    ax.set_title("CKD self-absorption")
    ax.set_yscale("log")
    fig.savefig(out_file+".pdf", dpi=300, bbox_inches='tight')
        
if __name__ == "__main__":

    inp = sys.argv[1]
    out = sys.argv[2]

    main(inp,out)