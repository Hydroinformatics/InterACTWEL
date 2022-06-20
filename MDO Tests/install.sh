# Setup scipt for openmdao and pyopt drivers
echo "Starting Installation of OpenMDAO and pyOPT"
echo "Requires administrator privileges to install OpenMDAO library and Non-Genetic Algorithm"
echo "*********************************************************"
echo ""

# Get pyopt files and openmdao library installation files.
git clone https://github.com/mdolab/pyoptsparse.git
sudo python pyoptsparse/setup.py install
sudo pip install openmdao

# For compilation errors or no fortran found uncomment below lines :-
# sudo apt-get update
# sudo apt-get install g77
# sudo apt-get install gfortran

# For errors persisting to openmdao or mpi4py uncomment below lines :-
# git clone http://github.com/OpenMDAO/OpenMDAO
# sudo pip install OpenMDAO/.
# sudo apt install libopenmpi-dev
# sudo apt-get install mpi4py

echo "*********************************************************"
echo "End of Install Script"
echo ""
echo "If you had no errors, You can proceed to run the files as normal."
echo "Otherwise fix the errors."
echo "vim install.sh file and check and uncomment specific lines related to errors."