# A Performance Prediction Model for Structured Grid Based Applications in HPC Environments

Md Bulbul Sharif

*Computer Science Tennessee Technological University* Cookeville, TN, USA msharif42@tntech.edu

Mario Morales-Hernandez ´ *Computational Science and Engineering Oak Ridge National Laboratory* Oak Ridge, TN, USA mmorales@unizar.es

Thomas Hines *Computer Science Tennessee Technological University* Cookeville, TN, USA tmhines42@tntech.edu

# Tigstu Dullo

*Civil and Environmental Engineering Tennessee Technological University* Cookeville, TN, USA ttdullo42@tntech.edu

Sheikh Ghafoor *Computer Science Tennessee Technological University* Cookeville, TN, USA sghafoor@tntech.edu

# Alfred Kalyanapu

*Civil and Environmental Engineering Tennessee Technological University* Cookeville, TN, USA akalyanapu@tntech.edu

*Abstract*—Predicting the performance of parallel applications at scale is a challenging problem. We have developed a performance prediction model for structured grid-based scientific applications for High Performance Computing systems. Our model can capture the system complexity and consider computation and communication attributes of application performance on HPC architectures. We have also proposed a methodology for obtaining the realistic value of the model parameters by small-scale sample runs of an application on the target system. We have used our model to predict the performance of an actual application (2D Flood Simulation) and a synthetic application (Game of Life) on the Summit supercomputer at Oak Ridge National Laboratory and Stampede2 at Texas Advanced Computing Center. The experimental results indicate that our model's predictive performance is acceptable, and our model was able to predict the performance of these two applications on Summit and Stampede2 with more than 90% accuracy.

*Index Terms*—Performance Prediction Model, BSP-Model, GPU, MPI, Summit, Stampede2.

## I. INTRODUCTION

Modeling the performance of parallel applications is a challenging task. Researchers have been developing models for parallel computing in general and performance prediction models for specific applications or architectures. The primary purpose of general models is to provide a standard way to define and assess parallel applications' performance. On the other hand, performance prediction models' primary focus is on an application's performance when executed on a machine. An application's scalability is determined by the gain in compute time versus the increase in parallel overhead as problem size and the number of processors increase. Several factors affect this overhead. Notably among them is the cost of communication and synchronization between the processors.

Developing a performance prediction model is challenging because of several factors. The architectures are increasingly heterogeneous concerning processing elements and interconnects between the processing elements. In addition, most modern HPC systems now contain traditional CPUs and GPUs as the primary computing elements. The computing capability and memory hierarchy vary between these two types of computing elements. Nodes in an extensive HPC system are organized in racks and connected using highperformance interconnect networks. The communication cost between processes running on two nodes on the same rack differs from processes running on two nodes on different racks.

Researchers have proposed models that abstract applications and architectures in few parameters, ignoring the specific details of the architecture. The most famous of them is the Bulk Synchronous Parallel (BSP) model [1]. Its primary objective is to bridge software and hardware, representing various architectures without considering hardware specifics. The BSP model identifies three characteristics of a machine: a collection of virtual processes, a point-to-point communication mechanism, and a global synchronization barrier. Another popular model is LogP [2], which lacks explicit synchronization and has implemented a more confined message-passing technique so that the network capacity limit is enough for communication load. The LogGP [3] model improves the LogP model for long messages, as many modern parallel machines have excellent support for long messages and a much higher bandwidth for long messages compared to short messages. These models are general, elegant, and helpful in developing algorithms or applications. However, these models are not very useful for performance prediction because they ignore many architecture and application attributes that impact the performance when executing the application on a real system. Moreover, these high-level abstractions do not represent real systems as they combine too many contributing factors into one parameter.

On the other hand, researchers have developed models [4], [5] for a specific application on a particular architecture that is more accurate than the generalized ones as these models often have more parameters. It is hard to obtain realistic values of the model parameters for performance prediction as architecture and execution environments change. Besides, many of these models are application-specific and are not portable across applications. However, these models provide better prediction capabilities than the widely applicable general-purpose parallel computing models such as BSP or LogP. Researchers and domain scientists have to pay either in terms of money or allocation and reserve resources in advance to run their application at scale on the HPC systems. They often have to run an application multiple times with different configurations and/or with different inputs. A model that abstracts the architecture in a few parameters is application-independent or at least applicable to a class of applications and can predict the performance with reasonable accuracy would be very beneficial to the researcher before they reserve resources of HPC and run their applications.

This paper presents a performance prediction model that is more detailed than the existing high-level models but simpler than the application or system-specific models. Our model works as a bridge between detailed application and/or architecture-specific models and general parallel computing models. It targets a class of applications (structured gridbased iterative scientific applications) that follows the same computation pattern and communication strategy. The model abstracts the underlying compute device and the communication in a few parameters and is pragmatic. We also propose a methodology to obtain the value of the model parameters such as per cell computation time and inter-process communication time by a few small-scale sample execution of an application on the target architecture. We have validated our model by predicting the performance of a real application (2D Flood Simulation) and a synthetic application (Game of Life) on the Summit and Stampede2 with more than 90% accuracy.

## II. PROPOSED MODEL & METHODOLOGY

Our model targets structured grid-based scientific applications. The base unit of a structured grid-based application is the cell. These cells are generally organized into a grid of two or three dimensions, each containing information about different variables at a particular location and at a specific time. A cell may use the neighboring cells' values and its own value to calculate its value for the next iteration. Formally, a stencil is known as the set of neighboring cells that are used to update the value(s) of a cell. For instance, in the 2D Game of Life [6], the stencil is the eight cells edging adjacent and diagonally adjacent to the cell that updates.

For running structured grid applications in a distributed environment the grid is usually divided among processors. As a result, the cells on the edge of a local grid have neighbors in a different processor, which is an issue as the neighbor cells are needed to calculate the next iteration. A standard solution is to consider the local grid containing all the cells that the processor is in charge of updating, plus the neighbors to those cells. These edge cells are known as halo cells, and the processor does not update them, but another processor does. Between iterations, other processors must update the halo cells. This procedure refers to as the "Halo Exchange". The computational pattern of a parallel structured grid scientific application is then: 1) Initialize grids, 2) Partition grids, 3) Compute iteration, 4) Update halo cells, and 5) Post-process the partitions. Steps 3 and 4 repeatedly continue until the computation finishes. Figure 1 shows the general flow diagram of such an application.

![](_page_1_Figure_6.png)

Fig. 1: Flowchart of a structured grid scientific application

## *A. Proposed Model*

For developing the model we can define Kw to be the average number of cells computed by a processor in unit time during an iteration. After each iteration, the halo cells (H) will be needed to be packed and unpacked for transfer between neighboring CPUs, where Oh represents the average time needed per packing and unpacking. There will also be some overheads (Ow) that do not depend on the number of cells such as synchronization and/or kernel calling overhead in a GPU-based application. If we define total computation time as Tw, this leads to:

$$T_{w}=\sum_{i=1}^{I}\left(\frac{C}{PK_{w}}+HO_{h}+O_{w}\right)\tag{1}$$

where C is the total number of cells in the global grid, H is the number of halo cells per process, I is the number of iterations, and P is the processor count. Communication time depends on the number of halo cells exchanged. We assume that messages are sent and received between neighboring CPUs simultaneously. Using the latency plus bandwidth model of communication, we can model the communication time (Tc) as follows:

$$T_{c}=\sum_{i=1}^{I}\left(\frac{H}{K_{b}}+O_{l}\right)\tag{2}$$

where Kb represents the communication bandwidth between any two processors and Ol represents the communication latency. We assume that pairwise halo exchanges between different sets of processors can occur in parallel, and these exchanges do not impact each other's performances. Thus, Tc is invariant to the total number of processors and works in weak scaling mode. We model the other overheads, such as grid initialization and program startup, as follows:

$$T_{o}=\sum_{i=1}^{I}O_{i}+CO_{c}+O_{s}\tag{3}$$

Oi represents any miscellaneous time taken per iteration not captured by Tw or Tc and Oc is the per cell time it takes to initialize the grids at the start of the simulation. Os accounts for other program startups that do not depend on the number of cells. The total time Tt taken for the application should then be:

$T_{t}=T_{w}+T_{c}+T_{o}$

TABLE I: Summary of the problem and unknown parameters

| Unknown Parameters |
| --- |
| Kw = Number of cells computed in unit time |
| Kb = Communication bandwidth |
| Oh = Per cell packing and unpacking time |
| Ow = Synchronization and kernel overhead |
| Ol = Communication latency |
| Oi = Miscellaneous time per iteration |
| Oc = Per cell grid initialize time |
| Os = Program startup time |
| Problem Parameters |
| C = Number of cells |
| P = Number of processors |
| I = Iteration count |
| H = Halo cells count |

Table I summarize all of the problem parameters and unknown parameters described in equation 1, 2, and 3.

#### *B. Model Parameter Estimation Methodology*

We can estimate the parameters in table I by small-scale sample runs of the applications on the target architectures by varying the grid's dimensions, the number of iterations, and the number of processors. We can measure the computation time, the communication time, and the total time taken for each run. This will allow us to consider Tw, Tc, and To independently. By using the inverse of Kw and Kb, each time Tw, Tc, and To is a linear combination of the unknown parameters, which allows the use of linear regression to find the parameters.

There is a significant variation in total compute time Tw when we change the number of processors from 1 to 2 or 2 to 4 as compared to changing the processor from, say, 16 to 20. Unfortunately, as written equation (1) does not give a good fit with linear regression because the long run times on the lower number of processors influence the best-fit line. Therefore instead of total compute time Tw, we can consider compute time per iteration which will not have a notable variation in the low number of processors. Therefore, we have used a modified but equivalent equation to fix this, (5), where P Tw/I does not have as much variability as the number of processors changes.

$$\frac{PT_{w}}{I}=\frac{C}{K_{w}}+PHO_{h}+PO_{w}\tag{5}$$

We can use the estimation of the unknown parameters to seed the model for predicting large-scale simulation on larger processors count. Besides, this information can help determine how many processors to run the simulation on, as we know the trade-off effect in computing resources versus time.

# III. APPLICATIONS

Specific applications will deviate slightly from the general model. We can add parameters to account for the work not accounted for in the general model. This paper looks at two applications for performance prediction: Game of Life [6] and TRITON [7]. The first is a popular application used to understand cellular automata behavior in the HPC system. The latter is an actual research application that uses multiple kernel computations, and reduction and has a variable workload between processes and iterations. Our goal was to see how we could extend a standard general model to a specific application that may not follow the general model strictly. One of our significant contributions to this paper is to show how to work with variable workloads and predict performance at a reasonable margin. Using more than one real-life application would have been better, but the effort required to port those codes to Summit or Stampede2 would require more time and more allocation hours than was available to us. As a result, we have limited our effort to one real-life application and one standard synthetic application. We believe that these represent a large portion of stencil-type structured grid applications.

#### *A. Game of Life (GOL)*

The Game of Life, created in 1970 by the British mathematician John Horton Conway [6] is a cellular automaton. There is a grid of cells that are either dead or alive. The Game of Life does not do anything beyond the general stencil grid model, so we do not need to modify any equations.

## *B. TRITON*

Two-dimensional Runoff Inundation Toolkit for Operational Needs (TRITON) [7] is a 2D hydrodynamic model based on the complete shallow water equations. It is an open-source flood simulation tool designed for HPC architectures and perfectly matches structured grid application criteria. In [8], [9], the authors provide more details on the numerical scheme and performance evaluation.

We choose TRITON because it deviates from the general stencil grid model in a few ways to give direction on how to tackle them. The first is that the work per cell per iteration is not constant (Kw). If the cell is marked dry, then most of the computation is skipped, which means that there is no single Kw for the application but a different one for each scenario as an average work per cell over the runtime of the simulation. As a result, two different flood event simulations on the same architecture may behave differently, although the underneath algorithm is the same. The second deviation is that TRITON dynamically picks the next timestep size based on the water height and velocity, which requires a global reduction that does not fit into any existing parameters. We assume the reduction is made efficiently with a binary tree and add lg(P)Kr in the communication equation where Kr represents the overhead of per reduction operation and P number of MPI processes.

$$T_{c}=\sum_{i=1}^{I}\left(\frac{H}{K_{b}}+O_{l}+lg(P)K_{r}\right)\tag{6}$$

Another effect of the dynamic step size is that we do not know how many iterations the simulation will run before running it. The solution to the varying Kw and the unknown iteration count is to run smaller simulations of the same scenario. We create a scaled-down elevation grid by averaging the heights of a square of cells and run this smaller simulation once. These scaled simulations of the same scenario then share the same Kw. They do not share the exact iteration count, but it does scale inversely with cell size. If there is a new scenario for predicting the runtime, we can run a much smaller version once and determine the Kw and iteration count. Then we can predict the actual runtime.

## IV. EXPERIMENTAL SETUP

# *A. Hardware Specifications*

All our GPU experiments use Summit [10] at Oak Ridge National Laboratory (ORNL). With two IBM Power 9 processors, 512 GB of DDR4 RAM, and six NVIDIA Volta V100 GPUs per node, Summit consists of 4608 nodes. We used up to 128 Summit nodes (768 GPUs) for our experiments. We used TACC's Stampede2 [11] for our CPU experiments. Stampede2 features 4200 Knights Landing (KNL) nodes, each has 68 cores, and each core has four hardware threads. We used up to 64 Stampede2 KNL nodes for our experiments.

#### *B. Benchmark Test Cases*

*1) Game Of Life (GOL):* We used six test cases to evaluate our Game of Life implementation with the randomly generated initial input. Table II summarizes all six test cases' characteristics. We used the Summit supercomputer for cases 4 to 6 and Stampede2 for cases 1 to 3.

*2) TRITON:* We used fourteen different test cases to evaluate TRITON, including four flood events and multiple grid resolutions for each flood event. Table II summarizes the characteristics of all the test cases. We executed the larger eleven test cases on Summit to utilize GPU and eight smaller ones on Stampede2.

## V. RESULTS AND ANALYSIS

All simulations used one MPI process per GPU and two MPI processes per node with 68 OpenMP threads per process in Stampede2. Our main focus is on large-scale multi-node applications, so we consider only inter-node communication and show results from 2 nodes. We will need an additional parameter to differentiate between inter-node and intra-node communication. All our experimental results showed here being used in a strong-scaling mode and are the average of 3 runs. There is a high variance of runtime described in figure 5b, and for that reason, it will be better if we have more runs to calculate the average. However, we had limited allocation hours on Summit and Stampede2. For example, a single run of Harvey (5m) simulation using 2 to 128 nodes requires more than 150 node hours (900 GPU hours) in Summit. We take the measured run times of different configurations and solve them using linear regression to fit the parameters. After that, we calculate the run time for a

# TABLE II: Characteristics of all test cases used for GOL and TRITON

|  | GOL |  |
| --- | --- | --- |
| Serial | No of Cells | Generation |
| 1 | 4,000,000 | 1,000,000 |
| 2 | 8,750,000 | 750,000 |
| 3 | 6,000,000 | 1,200,000 |
| 4 | 100,000,000 | 1,000,000 |
| 5 | 396,000,000 | 1,500,000 |
| 6 | 238,000,000 | 2,000,000 |
|  | TRITON |  |
| Serial | Name | No of Cells |
| 1 | Conasauga (60m) | 1,212,048 |
| 2 | Conasauga (30m) | 4,852,675 |
| 3 | Conasauga (15m) | 19,410,700 |
| 4 | Harvey (60m) | 1,890,063 |
| 5 | Harvey (30m) | 7,562,646 |
| 6 | Harvey (10m) | 68,080,474 |
| 7 | Harvey (5m) | 272,321,896 |
| 8 | Allatoona (40m) | 2,705,925 |
| 9 | Allatoona (20m) | 10,826,970 |
| 10 | Allatoona (10m) | 43,321,043 |
| 11 | Allatoona (5m) | 173,284,172 |
| 12 | Harris (20m) | 3,090,528 |
| 13 | Harris (10m) | 12,369,120 |
| 14 | Harris (5m) | 49,476,480 |

different test case by using the solutions. Finally, we compare the predicted value and the measured run time. There are eight unknown parameters (table I) in our general model (nine for TRITON), as a result, we need at least the same number of sample runs as the number of parameters to estimate the parameter using linear regression. After these initial sample runs, we only need one additional sample run for any new simulation on the same hardware and the same application.

## *A. GOL (Summit)*

Our first experiment uses test cases 4 and 5 of table II runtime values to determine machine parameters and predict case 6 runtimes of different nodes on Summit. We use three different runs of case 4 (2-8 nodes) and five runs of case 5 (2-32 nodes) to determine our unknown parameters. In GOL computation, we have to compute all cells, and there is no variation in workload for different test cases. Figure 2a shows GOL test case 6 prediction using 2 to 16 Summit nodes. The prediction is almost perfect here, with a computation time error within 5%. Communication error is 12% for one case when we use two nodes. Therefore, the total runtime error is always within 2%.

## *B. GOL (Stampede2)*

The second experiment uses test cases 1 and 2 of GOL to predict case 3 on Stampede2. We use ten run time results (5 each of the cases 1 and 2, 2- 32 nodes) for linear regression, and for the test, we also use nodes ranging from 2 to 32. In Figure 2b we see that there is more variance for GOL on Stampede2 compared to Summit. However, the computation time is within 7% and an underestimated communication time of 18% when we use 32 nodes. Besides, the total time is within 4% except for a 6.3% in the case of 4 nodes use.

![](_page_4_Figure_0.png)

Fig. 2: Predicted and Measured runtime of GOL in (a) Summit (b) Stampede2

#### *C. TRITON (Summit)*

For our third experiment, to predict test case 11 (Allatoona 5m, 173.3 million cells), we use a single run of case 8 (Allatoona 40m, 2.7 million cells) to determine the parameter Kw. We use five runtimes from the Conasauga flood event, 16 runtimes from the Harvey flood event, and seven from the Harris flood event ranging from 2 to 128 nodes to determine the other 8 unknown parameters. The Allatoona (5m) test case is 64x larger than Allatoona (40m).

Figure 3a shows predicted and measured time in terms of computation and communication. The predicted compute time is within 5%, while communication time is below 15%. The total predicted time is always within 4% of the actual time. For our fourth experiment, we use test case 7 (Harvey 5m), the largest test case with a total of 272 million cells. We use a single run of Harvey 60m (1.89 million cells), and the other three types of flood events measured run times to get the parameters. In that case, we use five runtimes from the Conasauga, 13 runtimes from the Allatoona, and seven from the Harris to fit our regression model. These results contain runtime from 2 nodes to 64 nodes. Harvey (5m) is

![](_page_4_Figure_5.png)

Fig. 3: Predicted and Measured runtime of TRITON in the Summit

144x larger than Harvey (60m), so this should result in the largest extrapolation error. Figure 3b shows the consistent underestimation of communication time. While the maximum computation error was 11% for two nodes, the maximum communication error was 19% for one node. The computing time was significantly more than the communication, so the total time error was only 11% maximum.

## *D. TRITON (Stampede2)*

In Stampede2, we use only two different resolutions, 4x larger than one another, for all the flood events. For our fifth experiment, we use a single run of case 1 (Conasauga 60m, 1.2 million cells) and the other three types of flood events measured run time to predict test case 2 (Conasauga 30m, 4.8 million cells). In that experiment, we use existing results from 33 different runs of Harvey, Allatoona, and Harris flood events to determine our unknown parameters. Those results are made use of 2 nodes to 64 nodes. Figure 4a shows that the predicted run time is consistent with the measured time, within 10%. However, the communication time is more variable than computation, with up to 22% underestimated.

![](_page_5_Figure_0.png)

Fig. 4: Predicted and Measured runtime of TRITON in the Stampede2

We use test case 13 (Harris 10m) for our final experiment, the largest test case on Stampede2, consisting of 12.4 million cells. We use a single run of Harris 20m (3.01 million cells), and the other three types of flood events measured run times to get the parameters. To calculate the unknown parameter using regression, we use existing results from 31 different runtimes of Harvey, Allatoona, and Conosauga flood events to determine our unknown parameters. The number of nodes used for these results ranged from 2 to 64. Figure 4b shows that communication time differs by almost 10% in every case. While the maximum computation error was 18% for 16 nodes, the minimum communication error was 3% for two nodes. The maximum total time error was 13% in the 16-node case, mainly because of the high error in the prediction of the computation time.

## *E. Error*

Figure 5a shows the percentage error in the total time of all six experiments described above. All the errors are less than 11% except for 13% in 1 case of experiment 6, and most are less than 5%. Additionally, the average error across all experiments is 4.2%.

![](_page_5_Figure_6.png)

Fig. 5: (a) Percentage error of total time in all 6 experiments (b) MPI Halo Exchange time variation of different runs using the same configuration in Summit

## *F. Analysis*

From the result presented above, we can see that the predicted computation time is very accurate across the experiments, but the prediction for communication time was less accurate. Further investigation reveals that it is due to the much higher variance between runs. Figure 5b shows the time taken to exchange halos per rank for three separate runs with the same configuration and test case using 24 GPUs. As this run is on Summit, there are 6 MPI ranks per node, corresponding to the increased exchange times on ranks 6-7, 12-13, and 18-19. These inter-node communications are highly variable from run to run, with the maximum time taken varying from 147 seconds to 252 seconds. By looking at the nodes' hostnames, it appears that the long inter-node communication times occur when the communication is crossing cabinets and, in particular, when the cabinets are non-consecutive. Depending on the ranks' placement, this high variance limits our predictions' accuracy for the communication time, Tc.

One limitation of our model is that we need some existing real data to find the parameters. However, any new simulation runtime prediction is pretty fast once we have that. For example, in the case of TRITON, presume we have all the runtime data of three utterly different flood events, such as Conasauga, Allatoona, and Harris cases on Summit. Data collection takes 490 minutes to finish all the simulations using one to 64 Summit nodes. A completely new flood event needs to simulate in our case, Harvey. We need to run only one simulation of significantly lower resolution to find out the work per cell per iteration Kw for the Harvey simulation. To run Harvey (60m) on Summit using two nodes takes only 65 seconds. Now, using the Kw for Harvey, we can predict Harvey 30m to Harvey 5m (144x bigger than 60m), and the total runtime of all the Harvey simulations in Summit is 680 minutes using two nodes to 128 Summit nodes. If we see the node hours needed for our experiments and collect the initial test data (Test cases 2, 3, 9, 10, 11, 13, 14), it takes 77 Summit node hours. Now we can predict Harvey simulation runtimes, which may take 168 node hours. We can use the same 77 node hours data to predict the newer test case runtimes if we have an entirely new test case. Similar things are also true when we use Stampede2. Using test cases 1, 2, 4, 5, 8, and 9 to fit the model takes almost 145 node hours in Stampede2, varying from 2 to 64 nodes. However, by using an additional 1.5 node hours to simulate test case 12 using two nodes, we can predict the rest of the 131 node hours simulation runtime of test cases 12 and 13.

Another interesting observation from our experiments is that the increase in communication time is relatively lower than the decrease in computation time as the number of processes grows. In stencil computation bulk of the communication happens due to the halo exchange between neighboring processors; for example, in row-wise partitioning (as in our case), process Pi exchange halo with only two other processes (Pi+1 and Pi − 1) independent of the total number of processes. If two pairs of processes can communicate in parallel, the halo exchange communication time is invariant of the total number of processors and works in weak scaling mode. Thus, the communication time increases nominally. The nominal increase is due to increased synchronization costs for more processes as the number of processes increases.

# VI. RELATED WORKS

Developing a sufficiently accurate model to allow reasonable performance prediction has proved to be a difficult task. We can categorize performance modeling in many ways, including empirical evaluation, simulation, analytical modeling, and machine learning modeling. Empirical evaluation [12], [13] is a methodology for obtaining system information through the observation of experiments. These experiments require correct implementation and equivalent hardware since the findings rely on the observed ground reality. Simulation modeling [14], [15] focuses on memory hierarchy, communication buses, parallel ports, and accelerators. They test each block of the given codes, similar to how they execute on the target computer. Therefore, they need source codes when making predictions. Simulators like [16] and [17] can predict with high precision, but they also take a long time to produce the expected results. Their slow runtime and infrastructure costs are significant disadvantages.

Analytical modeling is constructing a series of equations to demonstrate a high-level abstraction of application behavior and hardware architecture. We can classify this type of modeling in two categories - manually derived [18]–[22] and automatically derived with statistical methods [4], [23]– [26]. Analytical modeling can be easy and rapid to analyze as it is reduced to a series of equations to resolve. The biggest downside of analytical modeling is that it restricts the prediction range. These models would give high prediction errors when the model equations cannot capture the actual behavior.

While analytical performance models become restrictive due to application dynamics and/or multi-component interactions, machine learning-based performance models [5], [27], [28] can be helpful. Machine learning (ML) methods do not require the underlying system or application knowledge. Although a machine learning approach is more applicable for different applications and GPU architectures than an analytical approach, execution time prediction is less accurate. In [19] the authors proposed a model based on the number of computations and memory accesses of the GPU, with additional information on cache usage obtained from profiling. In addition, there are other existing works [29]–[32] which also tried to develop a performance prediction model for applications targeting GPU architectures.

Our work focuses on making a simple analytical BSP model that evaluates various structured grid-based applications on different architectures. Our profiling techniques validate application behavior and set parameters for computing and communication processes in parallel applications. Similarly, the primary basis of our model is the number of computational and communication measures used by the application as the BSP model. This model has made it simple to parametrize and adapt well to any cellular automation program.

## VII. CONCLUSION AND FUTURE WORK

We have developed a performance prediction model for stencil grid-based applications, approximating the application and system characteristics with few parameters while predicting performance with acceptable accuracy. Our model abstracts the underlying computing device, whether it is CPU or GPU, using the parameter Kw (number of cells computed per unit time). We can estimate the value of this parameter using a small-scale sample run that captures the underlying architecture and any algorithmic variation of the compute time. We tested our model using a complex real-world and a synthetic application on multiple architectures and found excellent prediction accuracy. The accuracy of our model parameter estimation impacts the accuracy of the performance prediction, which in turn depends on choosing the proper small-scale sample runs. The small-scale run should be small enough not to require much resource or time. On the other hand, it should be big enough that the problem does not fit entirely in the cache and involve enough processors to capture the communication characteristics of the actual largescale run. The relative advantage of our proposed model is that it applies to all structured grid stencil applications, and it captures the application and target architecture parameters accurately. On the other hand, our proposed method requires carefully selected sample runs of the application on the target architecture to estimate the model parameter values. We have limited our model to stencil grid applications, simplifying things as the computation and communication are regular and ordered. In general, an application could have arbitrarily complex computation and communication patterns. Our prediction of communication time is less accurate than computation time prediction and needs further investigation. Even with the uniform communication pattern of a stencil grid, there is a deviation from our prediction. That may be because the parallel halo exchanges do affect each other. Another communication issue is the variance between runs, especially at a higher node count. We might need to move from a point prediction to an interval of predicted runtimes, better capturing how the nodes behave. In addition, our future efforts will consider optimization techniques like overlapping communication and computation.

#### REFERENCES

- [1] L. G. Valiant, "A bridging model for parallel computation," *Communications of the ACM*, vol. 33, no. 8, pp. 103–111, 1990.
- [2] D. Culler, R. Karp, D. Patterson, A. Sahay, K. E. Schauser, E. Santos, R. Subramonian, and T. Von Eicken, "Logp: Towards a realistic model of parallel computation," in *Proceedings of the fourth ACM SIGPLAN symposium on Principles and practice of parallel programming*. New York, NY, USA: ACM, 1993, pp. 1–12.
- [3] A. Alexandrov, M. F. Ionescu, K. E. Schauser, and C. Scheiman, "Loggp: incorporating long messages into the logp model—one step closer towards a realistic model for parallel computation," pp. 95–105, 1995.
- [4] B. J. Barnes, B. Rountree, D. K. Lowenthal, J. Reeves, B. De Supinski, and M. Schulz, "A regression-based approach to scalability prediction," pp. 368–377, 2008.
- [5] E. Ipek, B. R. De Supinski, M. Schulz, and S. A. McKee, "An approach to performance prediction for parallel applications," in *European Conference on Parallel Processing*. Springer, 2005, pp. 196–205.
- [6] M. Gardner, "Mathematical games: The fantastic combinations of john conway's new solitaire game "life"," *Scientific American*, vol. 223, no. 4, pp. 120–123, 1970.
- [7] M. Morales-Hernandez, M. B. Sharif, A. Kalyanapu, S. K. Ghafoor, T. T. ´ Dullo, S. Gangrade, S.-C. Kao, M. R. Norman, and K. J. Evans, "Triton: A multi-gpu open source 2d hydrodynamic flood model," *Environmental Modelling & Software*, vol. 141, p. 105034, 2021.
- [8] M. B. Sharif, S. K. Ghafoor, T. M. Hines, M. Morales-Hernandez, ¨ K. J. Evans, S.-C. Kao, A. J. Kalyanapu, T. T. Dullo, and S. Gangrade, "Performance evaluation of a two-dimensional flood model on heterogeneous high-performance computing architectures," in *Proceedings of the Platform for Advanced Scientific Computing Conference*. New York, NY, USA: ACM, 2020, pp. 1–9.
- [9] M. Morales-Hernandez, M. B. Sharif, S. Gangrade, T. T. Dullo, S.- ´ C. Kao, A. Kalyanapu, S. Ghafoor, K. Evans, E. Madadi-Kandjani, and B. R. Hodges, "High-performance computing in water resources hydrodynamics," *Journal of Hydroinformatics*, vol. 22, no. 5, pp. 1217– 1235, 2020.
- [10] OLCF, "Summit," 2022. [Online]. Available: https://www.olcf.ornl.gov/ summit/
- [11] TACC, "Stampede2 texas advanced computing center," 2022. [Online]. Available: https://www.tacc.utexas.edu/systems/stampede2

- [12] S. Fortune and J. Wyllie, "Parallelism in random access machines," in *Proceedings of the tenth annual ACM symposium on Theory of computing*. New York, NY, USA: ACM, 1978, pp. 114–118.
- [13] P. B. Gibbons, Y. Matias, V. Ramachandran *et al.*, "The queue-read queue-write pram model: Accounting for contention in parallel algorithms," *SIAM Journal on Computing*, vol. 28, pp. 638–648, 1997.
- [14] N. Binkert, B. Beckmann, G. Black, S. K. Reinhardt, A. Saidi, A. Basu, J. Hestness, D. R. Hower, T. Krishna, S. Sardashti *et al.*, "The gem5 simulator," *ACM SIGARCH computer architecture news*, vol. 39, no. 2, pp. 1–7, 2011.
- [15] P. S. Magnusson, M. Christensson, J. Eskilson, D. Forsgren, G. Hallberg, J. Hogberg, F. Larsson, A. Moestedt, and B. Werner, "Simics: A full
- system simulation platform," *Computer*, vol. 35, no. 2, pp. 50–58, 2002. [16] T. Austin, E. Larson, and D. Ernst, "Simplescalar: An infrastructure for
- computer system modeling," *Computer*, vol. 35, no. 2, pp. 59–67, 2002. [17] S. J. Wilton and N. P. Jouppi, "Cacti: An enhanced cache access and cycle time model," *IEEE Journal of Solid-State Circuits*, vol. 31, no. 5, pp. 677–688, 1996.
- [18] S. A. Jarvis, D. P. Spooner, H. N. L. C. Keung, J. Cao, S. Saini, and G. R. Nudd, "Performance prediction and its use in parallel and distributed computing systems," *Future Generation Computer Systems*, vol. 22, no. 7, pp. 745–754, 2006.
- [19] M. Amaris, D. Cordeiro, A. Goldman, and R. Y. de Camargo, "A simple bsp-based model to predict execution time in gpu applications," IEEE, pp. 285–294, 2015.
- [20] L. Carrington, A. Snavely, and N. Wolter, "A performance prediction framework for scientific applications," *Future Generation Computer Systems*, vol. 22, no. 3, pp. 336–346, 2006.
- [21] J. Zhai, W. Chen, W. Zheng, and K. Li, "Performance prediction for large-scale parallel applications using representative replay," *IEEE Transactions on Computers*, vol. 65, no. 7, pp. 2184–2198, 2015.
- [22] B. F. Cornea and J. Bourgeois, "A framework for efficient performance prediction of distributed applications in heterogeneous systems," The *Journal of Supercomputing*, vol. 62, no. 3, pp. 1609–1634, 2012.
- [23] S. M. Sadjadi, S. Shimizu, J. Figueroa, R. Rangaswami, J. Delgado, H. Duran, and X. J. Collazo-Mojica, "A modeling approach for estimating execution time of long-running scientific applications," in *2008 IEEE International Symposium on Parallel and Distributed Processing*. Miami, FL, USA: IEEE, 2008, pp. 1–8.
- [24] L. T. Yang, X. Ma, and F. Mueller, "Cross-platform performance prediction of parallel applications using partial execution," in *SC'05: Proceedings of the 2005 ACM/IEEE Conference on Supercomputing*. Seattle, WA, USA: IEEE, 2005, pp. 40–40.
- [25] C. Truchet, A. Arbelaez, F. Richoux, and P. Codognet, "Estimating parallel runtimes for randomized algorithms in constraint solving," *Journal of Heuristics*, vol. 22, no. 4, pp. 613–648, 2016.
- [26] W. Pfeiffer and N. J. Wright, "Modeling and predicting application performance on parallel computers using hpc challenge benchmarks," in *2008 IEEE International Symposium on Parallel and Distributed Processing*. IEEE, 2008, pp. 1–12.
- [27] P. Malakar, P. Balaprakash, V. Vishwanath, V. Morozov, and K. Kumaran, "Benchmarking machine learning methods for performance modeling of scientific applications," in *2018 IEEE/ACM Performance Modeling, Benchmarking and Simulation of High Performance Computer Systems (PMBS)*. Dallas, TX, USA: IEEE, 2018, pp. 33–44.
- [28] J. Bhimani, N. Mi, M. Leeser, and Z. Yang, "New performance modeling methods for parallel data processing applications," *ACM Transactions on Modeling and Computer Simulation (TOMACS)*, vol. 29, no. 3, pp. 1–24, 2019.
- [29] S. Lee, J. S. Meredith, and J. S. Vetter, "Compass: A framework for automated performance modeling and prediction," in *Proceedings of the 29th ACM on International Conference on Supercomputing*. New York, NY, USA: ACM, 2015, pp. 405–414.
- [30] T. T. Dao, J. Kim, S. Seo, B. Egger, and J. Lee, "A performance model for gpus with caches," *IEEE Transactions on Parallel and Distributed Systems*, vol. 26, no. 7, pp. 1800–1813, 2014.
- [31] K. Kothapalli, R. Mukherjee, M. S. Rehman, S. Patidar, P. Narayanan, and K. Srinathan, "A performance prediction model for the cuda gpgpu platform," in *2009 International Conference on High Performance Computing (HiPC)*. IEEE, 2009, pp. 463–472.
- [32] N. Ardalani, C. Lestourgeon, K. Sankaralingam, and X. Zhu, "Crossarchitecture performance prediction (xapp) using cpu code to predict gpu performance," in *Proceedings of the 48th International Symposium on Microarchitecture*, 2015, pp. 725–737.

