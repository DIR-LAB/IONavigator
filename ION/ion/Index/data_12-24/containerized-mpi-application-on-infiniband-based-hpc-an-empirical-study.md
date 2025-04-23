# Containerized MPI Application on InfiniBand based HPC: An Empirical Study

Mandeep Kumar *University Institute of Computing Chandigarh University* Mohali, India *Locuz Enterprise Solutions Ltd.*  Delhi, India https://orcid.org/0000-0002-4851-4719 themandeepkumar@gmail.com

*Abstract*—**Nowadays, containerization techniques for High Performance Computing (HPC) are becoming more prominent with the increase in the features and complexity of scientific applications. Message Passing Interface (MPI) applications have many dependencies in terms of other scientific libraries, new patches, new code versions, and bug fixes to effectively execute scientific workloads. The tasks of updating the version of the code, installing new patches, and troubleshooting build issues are very time-consuming and complicated. These problems are tackled by making MPI applications portable through the use of the containerization concept, which hides system-level dependencies and complexities. This work presents the challenges and approaches for building and executing containerized MPI applications on InfiniBand based HPC. The comprehensive performance evaluation of a containerized MPI application converted from Docker to Singularity is performed on HPC up to 880 MPI ranks using InfiniBand in reference to bare metal. In addition, profiling of MPI applications is done by running them in an isolated container environment on InfiniBand based HPC with 640 MPI ranks.** 

*Keywords*—**Containerization, Docker, High Performance Computing, InfiniBand, Message Passing Interface, Performance, Profiling, Singularity**

# I. INTRODUCTION

In research communities that value reproducibility of both scientific findings and computational environments, container-based technology for distribution and deployment of applications reigns supreme. One of the most widely used is Docker [1]. It cannot be easily adopted in most High Performance Computing (HPC) environments due to the root privilege required to execute Docker containers and associated security concerns, as well as the lack of native support for Message Passing Interface (MPI) and HPC job scheduler [2]. Singularity was developed to meet the needs of users and administrators in HPC environments for scientific workloads, as well as bring containers and reproducibility to scientific computing [3]. It performed better than Docker in terms of container-based virtualization for HPC, with less overhead and more reliable security guarantees [4]. It also allows using the same Docker container without modifying it, which eliminates security concerns. The use of Singularity container technology in support of traditional HPC applications is likely to grow as a result of these characteristics [5].

MPI based applications are dependent on other scientific libraries and tools. Development and bug fixing continue with new patches. Debugging build issues and updating

Gagandeep Kaur *University Institute of Computing Chandigarh University*  Mohali, India https://orcid.org/0000-0002-1513-8446 gagandeepkaurlogani@gmail.com

application versions or patches takes time. Containerized MPI applications appear to be a promising way to hide system-level and dependency complexities while still allowing applications to be portable. As a result of the specific workloads based on MPI, its complex characteristics, multi-node distributed memory environment, and specific InfiniBand interconnect requirements, the following three concerns need to be examined: **(1) What are the challenges and potential directions for building and executing containerized MPI applications on InfiniBand based HPC? (2) Does the performance of a containerized MPI application converted from Docker to Singularity match that of a bare metal installed application on an InfiniBand based HPC? (3) How can the overall performance characteristics of a containerized MPI application on an InfiniBand based HPC be evaluated?**

The work's contributions are listed below,

- x Examining the most recent works of containerized applications for HPC environments.
- x We present the challenges and approaches for building and executing containerized MPI applications on InfiniBand based HPC.
- x We provide a comprehensive performance evaluation of containerized MPI application converted from Docker to Singularity and compare them to bare metal using InfiniBand on HPC.
- x We evaluate the overall performance characteristics of MPI application running in an isolated container environment on an InfiniBand based HPC.
- x We discuss open issues of Singularity for InfiniBand based HPC.

#### II. LITERATURE REVIEW

Various studies done in the past in this area can be found in the literature to find promising methods of containerization for HPC environments. Xavier et al. [4] examined the performance of container-based virtualization for HPC and found Singularity had less overhead than Docker while still providing more reliable security guarantees. Zhang et al. [6] pinpoint the performance bottleneck for MPI applications running in container-based HPC clouds and propose a high-performance locality-aware MPI library to address it. Younge et al. [7] discussed the use of containers for supercomputer and HPC system software and proposed a parallel MPI application DevOps model. Saha et al. [8] investigated the performance of Docker and Singularity on bare metal nodes in the Chameleon cloud, discussed a mechanism for mapping Docker containers to InfiniBand hardware using RDMA communication, and examined the mapping elements of parallel workloads to containers.

Zhang et al. [9] proposed a four-dimensional evaluation methodology to evaluate performance and illustrate that the Singularity container can achieve near-native performance. Torrez et al. [10] compared the performance of the three most popular HPC container technologies, Charliecloud, Shifter, and Singularity, to bare metal, Xu et al. [2] and Wang et al. [11] compared the performance of real-world applications running inside and outside of containers, with all three finding no significant difference in performance. Rudyy et al. [12] compared the performance of three different container technologies, which are Docker, Singularity, and Shifter, to native execution and found Singularity to be the best container technology for an HPC environment.

Liu et al. [13] compared and analysed the performance of multi-container deployment schemes for HPC workloads on a single-node platform, taking into account various containerization technologies such as Docker and Singularity. Liu et al. [14] studied the impact of container granularity on the performance of multi-container deployments using a variety of network fabrics and protocols, with an emphasis on InfiniBand networks. Ruhela et al. [5] discussed their early experiences on the petascale Frontera system running three cutting-edge containerization technologies and examined the performance of Charliecloud and Singularity containers. Hursey [15] explored the impact of two opposing container launch models on MPI libraries, as well as the cross-version compatibility between libraries interacting across the container boundary.

This work contributes, in various ways, to other works in the literature. Here we present the challenges and approaches to building and executing containerized MPI applications on InfiniBand based HPC. We provide a comprehensive performance evaluation of containerized MPI application converted from Docker to Singularity and compare them to bare metal on InfiniBand based HPC. We evaluate the overall performance characteristics of MPI application running in an isolated container environment on an InfiniBand based HPC. For the InfiniBand interconnect, we discuss open issues of Singularity.

## III. BACKGROUND

This section introduces containerization technologies, particularly Docker and Singularity, as well as InfiniBand based HPC and MPI.

## *A. Docker*

The most widely used containerization technology, Docker, is based on resource isolation and some kernel-level technologies, such as namespaces, cgroups, and a copyon-write filesystem [1]. It also includes OverlayFS, a unioncapable file system. Docker contains a lightweight engine to control and manage its containers, which eliminates the need for a hypervisor, which is required for virtual machines [13, 14].

## *B. Singularity*

Singularity was created to meet the demands of users and administrators in the HPC environment for scientific application-driven workloads [3]. In terms of container-based virtualization for HPC, it outperformed Docker, with less overhead and more reliable security guarantees [4]. Without the security concerns, Singularity allows using the same Docker container without making any changes. As a result of these characteristics, the use of Singularity container technology in support of traditional HPC applications is likely to grow [5].

## *C. InfiniBand based HPC*

High Performance Computing (HPC) is the primary foundation of scientific workload because of the complexity of research and the parallel computation capability required to complete it within the time frame. By utilising applications that require high bandwidth, enhanced networking, and extremely high compute capabilities, HPC allows scientists and engineers to solve complex science, engineering, and business problems [16]. InfiniBand is a switched fabric design that is used to connect nodes in HPC clusters [6]. InfiniBand interconnects are used for setting up multi-node clusters, which impact the performance of HPC workloads [17].

#### *D. MPI*

The Message Passing Interface (MPI) is a communication protocol that defines the user interface and functionality of a standard core of library routines for a wide range of messagepassing capabilities in terms of syntax and semantics [18]. It's widely used in the development of HPC applications.

#### IV. EXPERIMENTAL SETUP

This section describes the experimental setup for building, executing, evaluating, and profiling containerized MPI applications.

## *A. Hardware*

Our experiments are executed on a twenty-two node InfiniBand based HPC. Each host is equipped with 2x Intel (R) Xeon (R) Gold 6230 CPUs (20 cores each, hyperthreading disabled), 384 GB of RAM, 163 TB Lustre parallel file system, 1-Gigabit Ethernet network, and Mellanox InfiniBand (100Gb/s Adapter), which works on datagram mode.

# *B. Software*

For both hosts and containers, we use CentOS release 7.7.1908 with a host kernel 3.10.0-1062.el7.x86_64 and MLNX_OFED_LINUX-4.7-3.2.9.0 as the HCA driver. All the experiments were conducted on Docker 19.03.15 and Singularity 3.7.2 [19, 20]. SLURM 20.11.8, an HPC job scheduler, is used to submit container-based jobs to multinode clusters [21]. For MPI and compilation, Intel oneAPI Base and HPC Toolkit based Intel Compiler and MPI Version 2021.1 Build 20201112 are used [22, 23].

## *C. MPI Application and Benchmark Input File*

The GROMACS (GROningen MAchine for Chemical Simulations) package is a well-known and popular molecular dynamics software [24]. For multi-node distributed memory, it uses the standard MPI communication protocol. All the experiments are carried out with GROMACS 2021.1, and the 0768 directory and pme.mdp of the water_GMX50_bare input dataset, which is downloaded from the GROMACS ftp, are used as the benchmark input files [25, 26].

#### *D. Perfromance Analysis Tool*

The MPI usage patterns of the benchmark are profiled using Intel VTune Profiler [27]. We took an overall performance snapshot that included MPI and OpenMP usage and imbalance, memory access efficiency, vectorization, I/O, memory footprint, and floating-point throughput, as well as a rank-to-rank communication matrix to find out more about message passing.

# V. MPI APPLICATION CONTAINER CREATION AND EXECUTION

In this section, we describe the challenges and approaches for building and executing containerized MPI applications on InfiniBand based HPC. For the sake of experiments, we are using GROMACS as an MPI based application.

# *A. Container Creation*

To build the Docker image, a Dockerfile is required. A Dockerfile is simply a text-based script that contains instructions for creating a container image. It is necessary to write application installation instructions in the appropriate attributes and save them as the Dockerfile name without any extension. To create a Docker image, use the command docker build -t image-name:image-tag -f ./Dockerfile.

Singularity Definition File is a set of instructions that explain how to build a custom container. It is similar to a Dockerfile. Application installation instructions must be written in the appropriate attributes and saved as a Singularity file with any name and .def extension. To create a Singularity image, use the command singularity build --notest imagename.sif singularity-file.def.

In our experiments, we created a Dockerfile for GROMACS and used it to build a Docker image, which we uploaded to our Docker Hub account using docker push command.

# *B. Docker to Singularity Container Conversion*

Singularity enables the use of the same Docker container without any changes. A Docker image can be easily converted to a Singularity image using the singularity build command. Give the Docker image as, docker://<dockerhub-username>/<imagename>:<image-tag>.

We used the singularity build command in our experiments to convert our created and uploaded GROMACS Docker image directly to the Singularity image from Docker Hub.

# *C. Singularity Container Execution*

There are some challenges to using InfiniBand in Singularity. Use the same Linux operating system (OS) version for both hosts and containers, and for running containerized applications converted from Docker to Singularity, use the singularity exec command with the -B /usr/lib64, /etc/libibverbs.d option for binding InfiniBand driver libraries into the container, which required for use of InfiniBand on HPC. This can be used in HPC job scheduler scripts just like any other HPC application; we used SLURM job scheduler to submit jobs to InfiniBand based HPC.

The process approaches from container creation to execution for MPI applications on InfiniBand based HPC is depicted in Fig. 1. There are two approaches, each of which is described below in detail.

Approach 1: Generate a Singularity image from a Docker image and run it on an InfiniBand based HPC.

- x In the appropriate attributes, write the application installation instructions and save them as a Dockerfile name without any extension.
- x Build a Docker image using Dockerfile with the help of the docker build command.
- x Upload the built Docker image to Docker Hub or Private Registry with the help of docker push command.
- x Using the singularity build command, convert the created and uploaded Docker image to a Singularity image from the Docker Hub or Private Registry.
- x Use the HPC job scheduler to run the Singularity image, bind the InfiniBand driver libraries to the container for InfiniBand on the HPC, and execute it with the help of the singularity exec command.

Approach 2: Direct creation and execution of Singularity images on InfiniBand based HPC.

- x In the appropriate attributes, write the application installation instructions and save them as a Singularity file with any name and .def extension.
- x Create a Singularity image using the Singularity file with the help of the singularity build command.
- x Use the HPC job scheduler to run the Singularity image, bind the InfiniBand driver libraries to the InfiniBand container on the HPC, and execute it using the singularity exec command.

For the performance evaluation, the experiment setup has been done on the basis of approach 1, along with the execution phase of approach 2. The GROMACS application is containerized and converted from Docker to Singularity. The SLURM job scheduler is used to run the Singularity image on InfiniBand based HPC. On the production side, these approaches have been evaluated in the context of performance and profiling of containerized MPI applications for InfiniBand based HPC.

As the GROMACS is open and public, an optimized container of GROMACS 2021.1 for Intel AVX_512 has been uploaded to Docker Hub for performance evaluation and use. It can be accessed via docker pull mandeepkumar/gromacs:2021.1-avx-512 intel-sp-centos7.7 or directly convert from Docker to Singularity via singularity build gromacs-2021.1-avx-512-intel-sp-centos7.7.sif docker://mandeepkumar/gromacs:2021.1 avx-512-intel-sp-centos7.7. For performance analysis and use, an optimized debug enabled container of

![](_page_3_Figure_0.png)

Fig. 1. Process flow diagram for building containers and running them on an Infiniband based HPC.

GROMACS 2021.1 for Intel AVX_512 has been uploaded to Docker Hub and can be accessed via docker pull mandeepkumar/gromacs:2021.1-avx-512-

intel-sp-debug-centos7.7 or directly convert from Docker to Singularity via singularity build gromacs-2021.1-avx-512-intel-sp-debugcentos7.7.sif

docker://mandeepkumar/gromacs:2021.1 avx-512-intel-sp-debug-centos7.7.

## VI. MPI APPLICATION CONTAINER PERFORMANCE EVALUATION

In this section, we evaluate the performance of containerized GROMACS converted from Docker to Singularity and also compare the performance with bare metal on InfiniBand based HPC.

We scaled the performance of containerized GROMACS converted from Docker to Singularity using InfiniBand on HPC up to 880 MPI ranks, as the max available node and cores in our experimental setup, as shown in Fig. 2.

![](_page_3_Figure_8.png)

Fig. 2. Performance of containerized GROMACS converted from Docker to Singularity on InfiniBand based HPC.

The performance comparison results of containerized GROMACS converted from Docker to Singularity with bare metal is depicted in the Fig. 3. As can be seen, the difference is within the normal range of variation, which means it is not noticeable from a performance point of view, and we can consider containerized MPI applications converted from Docker to Singularity for InfiniBand based HPC.

Fig. 3. Performance comparison of containerized GROMACS converted

from Docker to Singularity with bare metal on InfiniBand based HPC.

# VII. MPI APPLICATION CONTAINER PERFORMANCE ANALYSIS

On InfiniBand based HPC, we examined the overall performance characteristics of containerized GROMACS converted from Docker to Singularity as an MPI application running in a separate container environment with 640 MPI ranks. To understand the general properties of a containerized MPI application, we used Intel VTune Profiler's Application Performance Snapshot.

The command line interface for VTune Profiler can be launched from the Singularity container. To profile an application, make sure the VTune Profiler is launched from the same container as the target application. Outside of the container, using the VTune Profiler for Singularity profiling is not supported.

Overall performance, including MPI and OpenMP usage and imbalance, memory access efficiency, vectorization, I/O, memory footprint, and floating-point throughput, is depicted in Fig. 4. This application is bound by MPI communication.

| MPI Time |  | Memory Stalls | Vectorization | Disk I/O Bound |  |
| --- | --- | --- | --- | --- | --- |
| 15.295 |  | 11.80% of pipeline slots | 93.05%of Packed FP Operations | 0.31% |  |
| 42.99%A of Elapsed Time |  |  |  | (AVG 0.11 sec, PEAK 0.15 sec). |  |
|  |  | Cache Stalls | Instruction Mix |  |  |
| MPI Imbalance |  | 7.89% of cycles | SP FLOPS | D/I | Read Write |
| 3.55 9.98% of Elapsed Time |  | DRAM Stalls | 94.37% of uOps | AVG | 32.5 KB . 0.6 KB |
|  |  | 2.91% of cycles | Packed: 93.28% from SP FP | PEAK | 17.6 MB 36.8 KB |
| TOP 5 MPI Functions | ్రా | DRAM Bandwidth | 128-bit: 2.85% 256-bit: 1,88% |  |  |
| Altoal | 17.08 | Not Available | 512-bit: 88,56% - |  |  |
| Sendrecy | 15.88 | NUMA | Scalar: 6-72% from SP FP |  |  |
| Init thread. | 6.00 | | 18.49%A of remote accesses | DP FLOPs |  |  |
| Allreduce and a man | 1.08 |  | 3.04% of UODS |  |  |
| Beast | 1.01 |  | Packed: 16.80% from DP FP. 128-bit: 1.42% |  |  |
|  |  |  | 256-bit: 0.00% |  |  |
| Memory Footprint |  |  | 512-bit: 15.37% |  |  |
|  |  |  | Scalar: 83,20%A from DP FP |  |  |
| Resident Per node Per rank |  |  | Non-FP |  |  |
| PEAK 7402.25 MB 220.45 MB |  |  | 5.62% of uOps |  |  |
| AVG 7383,32 MB 184,58 MB |  |  | FP Arith/Mem Rd Instr. Ratio |  |  |
|  |  |  | 0.74 |  |  |
| Virtual Per node Per rank |  |  | FP Arith/Mem Wr Instr. Ratio |  |  |
| PEAK 221040.67 MB 5570.79 MB |  |  | 1.80 -- W |  |  |
| AVG 221005.77 MB 5525.14 MB |  |  |  |  |  |

Fig. 4. Intel VTune Profiler Application Performance Snapshot report for containerized GROMACS converted from Docker to Singularity.

Because the application is MPI bound, as shown in Fig. 4, we also generated a rank-to-rank communication matrix to obtain more information about message passing, for message sizes, data transfers between ranks or nodes, and time in collective operations, whose outcomes are depicted in Fig. 5.

![](_page_4_Figure_1.png)

Fig. 5. Intel VTune Profiler rank-to-rank communication matrix for containerized GROMACS converted from Docker to Singularity.

#### VIII. SINGULARITY LIMITATION FOR INFINIBAND

In our experiment, we used the same CentOS version on both the host and the container to use InfiniBand. Previous studies also used the same or a compatible operating system on both the host and container to use InfiniBand [2, 13, 14].

We tried a few different approaches to providing supported InfiniBand driver details on Singularity from both outside and inside the container, but Singularity for InfiniBand does not support different Linux distributions and kernel version combinations for the host and container, this is still an open issue.

#### IX. CONCLUSION AND FUTURE WORK

In this work, the containerized MPI application is converted from Docker to Singularity and scaled up to 880 MPI ranks using InfiniBand on HPC. The proposed approach has no leakage, and the variation in results is within the normal range when compared to bare metal. As a result, MPI applications can be containerized for easy portability without sacrificing performance. Aside from that, we assessed the overall performance characteristics of an MPI application running in an isolated container environment on an InfiniBand based HPC with 640 MPI ranks. Furthermore, it has been demonstrated experimentally that profiling of containerized MPI applications using InfiniBand can be done effectively. In the future, this work can be extended to different Linux distributions for host and container to use InfiniBand.

#### ACKNOWLEDGMENT

This work is supported by Locuz Enterprise Solutions Ltd. (https://www.locuz.com). Thanks to the HPC Technology Team of Locuz for the support and valuable suggestions.

#### REFERENCES

- [1] D. Merkel, "Docker: lightweight linux containers for consistent development and deployment," *Linux Journal*, 2014(239), 2.
- [2] R. Xu, F. Han and N. Dandapanthula, "Containerizing HPC Applications with Singularity," HPC Innovation Lab. October 2017. [Online]. Available: https://downloads.dell.com/manuals/allproducts/esuprt_software/esuprt_it_ops_datcentr_mgmt/highcomputing-solution-resources_white-papers10_en-us.pdf
- [3] G. M. Kurtzer, V. Sochat and M. W. Bauer, "Singularity: Scientific containers for mobility of compute," *PLoS ONE* 12(5): e0177459.
- [4] M. G. Xavier, M. V. Neves, F. D. Rossi, T. C. Ferreto, T. Lange and C. A. F. D. Rose, "Performance Evaluation of Container-Based Virtualization for High Performance Computing Environments," in *Proc. 2013 21st Euromicro International Conference on Parallel, Distributed, and Network-Based Processing*, pp. 233-240.
- [5] A. Ruhela, M. Vaughn, S. L. Harrell, G. J. Zynda, J. Fonner, R. T. Evans, and T. Minyard, "Containerization on Petascale HPC Clusters," [Online]. Available: https://sc20.supercomputing.org/proceedings/sotp/sotp_files/sotp120s 2-file1.pdf
- [6] J. Zhang, X. Lu and D. K. Panda, "High Performance MPI Library for Container-Based HPC Cloud on InfiniBand Clusters," in *Proc. 2016 45th International Conference on Parallel Processing (ICPP),* pp. 268-277.
- [7] A. J. Younge, K. Pedretti, R. E. Grant and R. Brightwell, "A Tale of Two Systems: Using Containers to Deploy HPC Applications on Supercomputers and Clouds," in *Proc. 2017 IEEE International Conference on Cloud Computing Technology and Science (CloudCom)*, pp. 74-81.
- [8] P. Saha, A. Beltre, P. Uminski and M. Govindaraju, "Evaluation of Docker Containers for Scientific Workloads in the Cloud," in *Proc.* Practice and Experience on *Advanced Research Computing (PEARC18),* ACM, New York.
- [9] J. Zhang, X. Lu, and D. K. Panda, "Is Singularity-based Container Technology Ready for Running MPI Applications on HPC Clouds?" in *Proc. 10th International Conference on Utility and Cloud Computing (UCC '17),* Association for Computing Machinery, New York, NY, USA, 151–160.
- [10] A. Torrez, T. Randles and R. Priedhorsky, "HPC Container Runtimes have Minimal or No Performance Impact," in *Proc. 2019 IEEE/ACM International Workshop on Containers and New Orchestration Paradigms for Isolated Environments in HPC (CANOPIE-HPC),* pp. 37-42.
- [11] Y. Wang, R. T. Evans and L. Huang, "Performant container support for HPC applications," in *Proc. Practice and Experience in Advanced Research Computing on rise of the machines (learning), PEARC'19,* pp 1–6. Association for Computing Machinery.
- [12] O. Rudyy, M. Garcia-Gasulla, F. Mantovani, A. Santiago, R. Sirvent and M. Vázquez, "Containers in HPC: A Scalability and Portability Study in Production Biological Simulations," in *Proc. 2019 IEEE International Parallel and Distributed Processing Symposium (IPDPS),* pp. 567-577.
- [13] P. Liu and J. Guitart, "Performance comparison of multi-container deployment schemes for HPC workloads: an empirical study," J *Supercomput* 77, 6273–6312 (2021).
- [14] P. Liu and J. Guitart, "Performance characterization of containerization for HPC workloads on InfiniBand clusters: an empirical study," *Cluster Comput* (2021).
- [15] J. Hursey, "Design Considerations for Building and Running Containerized MPI Applications," in *Proc. 2020 2nd International Workshop on Containers and New Orchestration Paradigms for Isolated Environments in HPC (CANOPIE-HPC),* pp. 35-44.
- [16] M. Kumar, "Combination of Cloud Computing and High Performance Computing," *Int. J. Eng. Comput. Sci* vol.5, no. 12, pp. 19545-19547, December 2016.
- [17] A. Ruhela, S. Xu, K. V. Manian, H. Subramoni and D. K. Panda, "Analyzing and Understanding the Impact of Interconnect Performance on HPC, Big Data, and Deep Learning Applications: A Case Study with InfiniBand EDR and HDR," in *Proc. 2020 IEEE International Parallel and Distributed Processing Symposium Workshops (IPDPSW),* pp. 869-878.

5

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:32:44 UTC from IEEE Xplore. Restrictions apply.

- [18] "MPI: A Message-Passing Interface Standard Version 4.0," [Online]. Available: https://www.mpi-forum.org/docs/mpi-4.0/mpi40-report.pdf
- [19] "Install Docker Engine on CentOS," [Online]. Available: https://docs.docker.com/engine/install/centos/
- [20] "Singularity 3.7.4," [Online]. Available: https://github.com/sylabs/singularity/releases/tag/v3.7.4
- [21] "SLURM Download," [Online]. Available: https://www.schedmd.com/downloads.php
- [22] "Intel oneAPI Base Toolkit," [Online]. Available: https://www.intel.com/content/www/us/en/developer/tools/oneapi/bas e-toolkit-download.html
- [23] "Intel oneAPI HPC Toolkit," [Online]. Available: https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc -toolkit-download.html
- [24] "About GROMACS," [Online]. Available: https://www.gromacs.org/About_Gromacs
- [25] "GROMACS 2021.1 Source code," [Online]. Available: https://doi.org/10.5281/zenodo.4561626
- [26] "GROMACS water_GMX50_bare input dataset," [Online]. Available: ftp://ftp.gromacs.org/pub/benchmarks/water_GMX50_bare.tar.gz
- [27] "Intel VTune Profiler," [Online]. Available: https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtu ne-profiler-download.html

6

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:32:44 UTC from IEEE Xplore. Restrictions apply.

