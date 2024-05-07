#PBS -N main
#PBS -q paralela
#PBS -l nodes=3:ppn=128
#PBS -e outputs/erros_paralela
#PBS -o outputs/saidas_paralela
#PBS -m abe
#PBS -M g229780@dac.unicamp.br

module load anaconda3
module load mpich/4.1.1-gcc-9.4.0

source phd3/bin/activate

cd $PBS_O_WORKDIR

mpirun python -m mpi4py.futures main.py
