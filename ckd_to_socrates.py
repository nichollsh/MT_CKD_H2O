import numpy as np
import sys, os
from netCDF4 import Dataset
import matplotlib.pyplot as plt

def once(in_file:str):

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
    out_file = in_file.replace(".nc","").strip()
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

    return out_file, nu, ab

if __name__ == "__main__":

    # all files in directory    
    if len(sys.argv) == 2:
        got = os.path.abspath(sys.argv[1])

        if os.path.isfile(got):
            inp = [got]
            dir = os.path.dirname(got)
        else:
            dir = got
            inp = [f for f in os.listdir(dir) if f.startswith("mt_ckd") and f.endswith(".nc")]
            
    else:
        print("Usage: python ckd_to_socrates.py <input_file.nc>")
        print("   or: python ckd_to_socrates.py <directory_with_nc_files>")
        sys.exit(1)

    # process all the files
    dat_arr = []
    for f in inp:
        print("Processing file: %s"%(f))
        dat_arr.append(once(f))

    # make plot 
    fig,ax = plt.subplots()
    for dat in dat_arr:
        lb = os.path.basename(dat[0])
        ax.plot(dat[1], dat[2], label=lb)

    ax.set_xlabel("Wavenumber (cm-1)")
    ax.set_ylabel("Continuum Absorption (cm^3.molec-1 * 1.0E-20)")
    ax.set_title("CKD Continuum Absorption")
    ax.set_yscale("log")

    # add reference wavelengths [nm]
    ref_wl = [400, 600, 1000, 2e3, 4e3, 6e3, 1e4, 1e5]
    for wl in ref_wl:
        nu = 1e7/wl
        ax.axvline(nu, color="gray", linestyle="--", alpha=0.5)
        ax.text(nu, ax.get_ylim()[0]*1.5, "%g um"%(wl/1e3), rotation=90, 
                verticalalignment="bottom", horizontalalignment="right", fontsize=8)


    ax.legend()
    plt.show()
    fig.savefig("mt_ckd_plot.pdf", dpi=300, bbox_inches="tight")

    print("Done.")
