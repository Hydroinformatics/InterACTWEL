#!/bin/bash 
#SBATCH -p cloud
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mail-user=sammy.rivera@oregonstate.edu
#SBATCH -o /export/output.stdout
#SBATCH -e /export/output.stderr

#SBATCH --mail-type=ALL

module load python3
/bin/python3 /export/src/sammy_mdao_results/Dummy/OpenMDAO_Dummy_Multiple_Basinsv8_time.py