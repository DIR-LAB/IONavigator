# **Enhance Virtualized HPC System Based on I/O Behavior Perception and Asymmetric Scheduling**

Yanyan Hu, Xiang Long, Jiong Zhang School of Computer Science and Technology, Beihang University, Beijing, China Email: huyanyan84@gmail.com, long@buaa.edu.cn, zhangjiong@buaa.edu.cn

*Abstract***—In virtualized HPC system such as virtual cluster and science cloud, CPU-intensive jobs are always companied by high-intensive I/O operations since different computing nodes perform periodic inter-VM communication to transfer data or synchronize computing result. Since traditional VMM schedulers cannot handle the scheduling scenario with mixed workloads efficiently, inter-VM communication always suffers serious performance regression from scheduling competition and then reduces the performance of entire virtualized HPC system. In order to address this issue, this paper proposes an asymmetric scheduling model based on I/O behavior perception. In this mode, we schedule I/O and computing jobs under isolated cpu subsets to erase their performance interference while optimizing the inter-VM communication through short period round robin scheduling. At the same time, we characterize the runtime I/O behavior of applications at fine temporal granularity and predict their I/O load state using specific online predictor. We will replan the scheduling scheme dynamically through migrating VMs across different cpu subsets if we predict a coming I/O intensity variation and decide the system performance could benefit from this scheduling adjustment. We build a prototype based on Xen-4.1.0 virtual and preliminary test results demonstrate that our approach could efficiently promote the performance of inter-VM communication under virtualized HPC environment while reducing the computing performance degradation caused by I/O-prior scheduling.**

#### *Keywords***-HPC; Virtualization; Cloud; Scheduling; I/O;**

# I. INTRODUCTION

Cloud computing has been tremendously growing not only for traditional commercial web applications but also for scientific applications. Many traditional HPC infrastructures are becoming increasingly virtualized to efficiently and safely share computing resources between different applications and services. However, there is an important challenge faced by future HPC platforms using virtualization technology: how to erase the performance bottleneck of inter-node communication caused by I/O virtualization. This bottleneck is caused by many reasons and scheduling confliction between I/O and computing jobs is an important one of them [1]–[3]. Since traditional virtual machine schedulers mostly focus on sharing the processor resources fairly among domains while leaving the scheduling of I/O resources as a secondary concern, the I/O performance of virtual machines always suffer serious degradation from disordered scheduling competition. Since I/O access especially network communication plays a key role in the HPC system, this performance regression could significantly reduce the capacity and stability of I/O subsystem and thus reduce the performance of virtualized HPC applications [4], [5].

Intuitively, I/O-oriented scheduling optimization could simply address this issue. However, most HPC applications are composed of both I/O and computing jobs which not only compete for system resource with each other but also have complicated dependence relationship. In this case, the performance of I/O and computing jobs must be balanced cautiously to achieve an optimized system configuration. Moreover, the strategy of VM scheduling also impacts many other aspects such as cache sharing, memory exchange efficiency across different VMs, lock management and synchronization. Therefore, scheduler optimization must consider all these factors to avoid inducing new bottlenecks into the system.

In order to optimize the VM scheduling under virtualized HPC system, this paper proposes an asymmetric virtual machine scheduling model based on dynamic I/O behavior perception. In this model, we deploy two individual cpu subsets to undertake I/O and computing jobs respectively. Then we track the runtime I/O behavior of applications through collecting the I/O event information from active virtual machines and try to perceive the variation of I/O load states. Virtual machines will be migrated across different cpu subsets if we predict a coming state transition and decide the system performance could benefit from this scheduling adjustment. Several important issues are discussed in this paper including the methodology of I/O state predicting and execution phase tracking, topology optimization of cpupool allocation and co-scheduling of cooperative virtual machines. We build a prototype based on Xen-4.1.0 system and preliminary test results demonstrate that our approach could efficiently balance the performance between communication and computing when virtualized HPC applications are run under CPU competition scenario.

The contributions of this paper are mainly listed as follows. First, we proposed a conception of asymmetric VM scheduling based on I/O behavior perception. Second, we designed a runtime behavior characterizing framework for virtualized HPC applications and exploited several important issues that affect I/O behavior analysis and predicting. Fi-

Table I NETWORK LATENCY OF INTER-VM COMMUNICATION

|  | min | max | average | stedv |
| --- | --- | --- | --- | --- |
| Credit | 35.989ms | 59.884ms | 48.893ms | 8.323ms |
| RR(30ms) | 31.474ms | 119.494ms | 54.150ms | 16.493ms |
| RR(0.5ms) | 1.211ms | 3.319ms | 1.793ms | 0.342ms |

nally, we discussed the possibility of resource allocation and scheduling optimization based on the correlation between multiple cooperative virtual machines.

The remainder of this paper is organized as follows. We first introduce some background of virtualized HPC system and discuss our motivation in Section II. Then we propose our scheduling model and detail several important mechanisms in section III. After that, we describe the implementation of our prototype system in section IV and evaluate our design in section V. We further discuss some other important issues about scheduling optimization of virtualized HPC system in section VI and introduce some related work in section VII. We finally conclude our job with a discussion and introduce our future works in section VIII.

# II. BACKGROUND AND MOTIVATION

# *A. HPC system based on virtualization and cloud computing*

Traditional HPC system were mostly built on single platform which has massive computing capacity but be difficult to be multiplexed and expanded. In this case, many customers' applications could be rejected because the HPC facilities may not grow at the same pace as the growing of computational demands. Recent years, virtualization technology provides a more efficient way to manage and multiplex computing resources and then contributed to the emergence of cloud computing which has become an alternative platform to bridge the gap between scientists' growing computational demands and limited local computing capabilities. On cloud environment, the capacity and structure of HPC system are desired to be adjusted dynamically according to the requirement of customers and the capability of traditional large computing system could be utilized more efficiently through being multiplexed to different users concurrently. Currently, we have seen an increasing adoption of cloud computing in a wide range of scientific disciplines, such as high-energy and nuclear physics, astronomy and climate research.

# *B. Performance regression of network communication*

In virtulized HPC system, computing nodes are deployed with individual virtual machines which connected by network. Although modern virtualization technology has been able to achieve near-native performance for pure computing jobs, I/O performance especially network capacity still has serious bottleneck in most cases. There are many factors that limit the I/O performance under virtualization environment and scheduling latency caused by CPU competition is an important one of them. Since most HPC applications always try to exhaust their CPU time while perform intensive interprocess communication, they would suffer serious network

![](_page_1_Figure_9.png)

 

 performance regression without self-virtualized hardware support. Current researches have proved that the performance regression of inter-nodes communication is the most serious issue that restrain the performance of virtualized HPC system [4], [5]. Many scholars have tried to address this issue through I/O-oriented scheduling optimization [6]–[9]. However, most HPC applications are composed of both I/O and computing missions which not only compete for system resource but also have complicated dependence relationship. Therefore, simple I/O-oriented scheduling optimization could break the balance between I/O and computing and then cause performance regression instead of promotion.

 In order to demonstrate the effect of performance balance between communication and computing and highlight some possible factors that could limit the scheduling optimization of virtualized HPC system, we modify the scheduler of Xen-4.1.0 virtual machine and perform several experiments to observer the performance variation under different scheduling configurations. We first replaced the Credit scheduler with a high frequent round-robin scheduler. This RR scheduler schedules each VCPU fairly with a fixed time scale and directly inserted them into the tail of run queue after time slice is exhausted. The scheduling period was set to 0.5ms and 30ms to compare the influence of different scheduling delays. We also modified the load balance mechanism of Xen Credit scheduler: it now just tries to balance the VCPU quantity between different CPU cores to avoid unnecessary VCPU migration which could cause unpredictable scheduling behavior. During this test, we deployed four virtual machines in a quad-core x86 server and perform NPB-3.3 [10] benchmark with four parallel processes using OpenMPI library. We bind these four VMs together and forced them to share 2 specific processor cores to construct a CPU competition scenario. We selected five different NPB programs for this test including LU, CG, SP, BT and EP program and used Class C problem size to achieve a proper data scale and total running time. We recorded the total running time of different NPB benchmarks and tested the latency of inter-VM communication when system ran.

As illustrated in Table I, the long-period(30ms) RR scheduler and Credit scheduler have similar unsatisfactory network latency which finally led to close NPB performance. By comparison, the network capacity significantly improved after short-period(0.5ms) RR scheduler was applied. The average ping latency reduced to 1.793ms while the stdev reduced to 0.342ms. However, we observed significantly distinction when we compared the performance improvement of different benchmarks. As illustrated in Figure 1, CG program gained more than 90% performance promotion which is the most one across all five programs. Compared to CG benchmark, SP and BT program got less performance improvements which are 37.6% and 31.9% respectively. LU got least performance promotion which is only about 22.5%. For EP program, the entire performance reduced about 12% rather than any improvement.

In order to explain this performance distinction and provide some insights on the fact, we characterized the I/O behavior variation of different NPB benchmarks by collecting their I/O event information at a granularity of 100ms. Each sampling period, we traced the I/O events sent to each virtual machine and calculated their I/O event frequency which finally reflected the I/O load intensity of applications. We illustrate test results of LU, CG, SP and EP programs in Figure 2 and excluded BT program here because it has very similar result as SP program. During this experiment, we did not explicitly distinguish disk and network I/O operations since disk access only happened at the beginning of program execution to load reference data. All other I/O operations are caused by network communication between cooperative virtual machines.

As illustrated in Figure 2, these programs exhibit significantly different I/O behaviors during their execution which actually reflect the algorithm and communication mode distinction [11]. LU benchmark applies SSOR algorithm to solve regular-sparse lower and upper triangular systems. Computing nodes perform fine-granularity pointto-point communication during each iteration and thus cause continuous but low-intensity I/O operations. The periodic high-intensity I/O states are caused by data transmission at the joint of two iterations since result data need to be synchronized before starting the next step calculation. CG benchmark uses a conjugate gradient method to compute an approximation to the smallest eigenvalue of a large, sparse, symmetric positive definite matrix. Different from LU, it performs intensive irregular collective communication across different nodes when executing sparse-matrix vector multiplication during each loop. Therefore, continuous highintensive I/O operations are observed during the execution and periodic low-intensive I/O states always appear at the end of each iteration. SP benchmark solves multiple independent systems of non diagonally dominant scalar pentadiagonal equations. Its communication is mainly composed of irregular point-to-point long message transmission and each process can perform computing work as soon as it receives data from other processes. Therefore, low-intensity I/O load states are always followed by irregular highintensity I/O operations which demonstrate the transmission of messages during the execution. EP benchmark, as the acronym suggests, is an "embarrassingly parallel" kernel. It requires virtually no inter-processor communication and only coordination of pseudo-random number generation at the beginning and collection of results at the end. Therefore, it produces little I/O operations during its entire execution.

This I/O behavior distinction finally causes the performance difference illustrated in Figure 1. CG benchmark gets most benefit from the improvement of network capacity because of its continuous and high-level communication intensity. By contrast, SP and BT benchmarks only perform periodical intensive inter-VM communications. Therefore, the overhead caused by the high frequency context switch partly offsets the performance improvement that benefits from RR scheduling and finally reduces the ratio of performance promotion. LU benchmark's average I/O intensity is even less than SP and BT programs and thus results in least performance promotion. For EP benchmark, the system gets non benefit from communication optimization since all computations are performed inside individual VMs. Therefore, it suffers most seriously from frequent context switch and finally causes noticeable performance degradation.

# *C. summary*

It is clear that the inter-VM communication is a crucial part of the virtualized HPC applications and its performance could significantly benefits from I/O-oriented scheduling optimization. However, because of the confliction between communication and computing, this optimization could also influence the execution of computing tasks and then reduce the efficiency of system. In this case, cautious scheduling balance between I/O and computing jobs would be an important basement to achieve an optimum configuration for virtualized HPC system. Since the I/O load state of applications always vary over time, accurate perception of I/O behavior with fine temporal granularity would be necessary for further scheduling optimization. This issue could be very difficult to be addressed for some cases such as web servers because of the strong variation and serious randomness of applications. Fortunately, most HPC applications have structural programming paradigm and communication model which lead to regular communication behavior. This regularity and potential periodicity could provide much convenience for runtime I/O behavior characterizing and then provide some possibility for dynamic scheduling decision. In the next section, we will describe our methodology of I/O behavior tracking and predicting and demonstrate how to use this information to optimize the performance of virtualized HPC applications based on asymmetric scheduling.

# III. ASYMMETRIC VIRTUAL MACHINE SCHEDULER BASED ON I/O BEHAVIOR TRACKING

There are 3 main goals of our design:

![](_page_3_Figure_0.png)

![](_page_3_Figure_1.png)

1. Reduce the I/O performance degradation especially network latency caused by scheduling competition using I/O-oriented scheduling optimization;

2. Limit the overhead of frequent context switch through runtime I/O behavior tracking and dynamic VM migration;

3. Coordinate the scheduling of multiple virtual machines based on their cooperative relationship;

In past research work, we have applied a multi-core dynamic partitioning method to realize a asymmetric scheduling framework under Xen-3.1.0 virtual machine [9]. Although this approach could efface the performance interference between I/O and computing in some degree, it also reduced the efficiency of scheduler because it just applied a simple reactive way to handle the I/O load variation of applications(a VCPU is always instantly migrated to I/O core when an I/O event is delivered). As introduced in Section II, the scheduling of I/O and computing jobs must be well balanced to achieve an optimal configuration for virtualized HPC system. Therefore, we should analyze the running state of system more cautiously before we making scheduling decision. In this study, we first try to predict the I/O behavior accurately and track different macro execution phases of applications. Then we make scheduling decision based on this analysis and try to maximize the effect of I/O optimization while limit the negative influence of frequent context switch through dynamic VM migration. We also attempt to optimize the scheduling of multiple virtual machines which coordinate for the same parallel program. This optimization could help to avoid some possible issues such as deadlock and synchronization latency. In following

172

![](_page_4_Figure_0.png)

Figure 3. Asymmetric scheduling model based on VM migration

sections, we will introduce our design and discuss these issues in detail.

## *A. I/O behavior predicting and execution phase tracking*

The first prerequisite to realize our design is tracking the I/O state of applications and providing necessary information for adaptive scheduling optimization. This tracking can be realized in either proactive or reactive ways. Traditional adaptation techniques usually operate in reactive manner because of its simplicity and better efficiency. However, reactive system always suffers by continuously lagging behind if application exhibits significant variability in its behavior. By contrast, proactive approach has better timeliness while needs more abundant history information and analysis to achieve an acceptable accuracy. As illustrated in Figure 2, I/O intensity variation of most programs exhibit noticeable transient characteristic during our test. In this case, reactive adaptation could not be able to capture this variation promptly and then miss the opportunity of scheduling adjustment. Therefore, in this paper we apply proactive methodology and predict the I/O load state of applications to provide some guides for further scheduling decision.

Currently, there have been many classic online predictors used for runtime behavior predicting. All of them have different complication and are fit for different cases. In order to select a proper predictor for our design, we applied four different algorithms including Last value, Exponentially weighted moving average(*EWMA*) [12], *Markov* model [13] and Run Length Encode predictor(RLE) [14] to our study cases and compared their precisions with both entirestate predicting and state-transition predicting. The entire precision is tested through the predicting hit rate which demonstrates the matching degree between prediction results and the actual ones. The precision of state transition depicts the sensitivity and temporal accuracy of predictors for state changing. A prediction of state transition is thought to be correct only when both origin and coming state match the actual ones. Test results are illustrated in Table II and III.

As demonstrated in Table II and Table III, simple statistic predictors(Last Value and EWMA) have worse precision than history-based predictors(Markov and RLE) because of their inherent defect of temporal-delay. At the same time, standard Markov predictor has better entire-state predicting precision then RLE predictor since the latter one has stronger

computing cpupool

Low I/O-intensity

I/O intensity

increasing

VMs migration

reached threshold

High I/O-intensity

Table II ENTIRE PREDICTING PRECISION OF STATE VALUE

|  | BT | CG | EP | LU | SP |
| --- | --- | --- | --- | --- | --- |
| LastValue | 50.4% | 89.9% | 99.6% | 85.9% | 49.1% |
| EWMA | 66.1% | 84.5% | 99.6% | 88.0% | 65.4% |
| Markov | 85.9% | 90.6% | 99.6% | 94.0% | 84.8% |
| RLE | 78.3% | 89.6% | 99.6% | 90.1% | 75.2% |

Table III PREDICTING PRECISION OF STATE-TRANSITION

|  | BT | CG | EP | LU | SP |
| --- | --- | --- | --- | --- | --- |
| LastValue | N/A | N/A | N/A | N/A | N/A |
| EWMA | 19.5% | 34.0% | N/A | 28.1% | 19.0% |
| Markov | 50.3% | 49.6% | N/A | 48.0% | 48.2% |
| RLE | 62.4% | 65.9% | N/A | 63.3% | 58.7% |

history persistence which could cause some erroneous prediction of state variation. However, its sensitivity of state changing also leads to a better accuracy of state-transition predicting, especially for those cases where programs have stronger periodicity and more long-term stable phases followed by abrupt I/O-intensity changing such as LU and CG benchmarks. Since our purpose of I/O behavior predicting is tacking different execution phases of applications and providing direction for VM scheduling, incorrect statetransition prediction could cause false phase tracking result and then lead to irrational scheduling adjustment. Therefore, the precision of state-transition predicting is actually more important. In this paper, we apply RLE model as our predictor since it has the best precision of state-transition predicting for our study cases.

RLE predictor [14] uses a run-length encoded version of the history to index into a prediction table. The table reference is a hash of the state value and the number of times that this state has occurred in a row. The lower bits of the hash function provide an index into the table while the higher bits provide a tag. Each predicting period, the tag will be checked. If there is a match, the value stored in the table entry will provide a prediction for the state of coming duration. If the tag match fail, the prior state is assumed to be the prediction result for next execution period which means no state-transition will happen. The hash table will be updated in two cases: (1)state value changes which means state-transition happens; (2)tag match which means a table entry need to be updated. In the first case, we directly insert a new entry into the hash table since we want to predict this state-transition before its next happening. Execution intervals where the same state continuously occurs will not be stored into the table since they will be correctly predicted as "last phase ID" when the table lookup missed. In the second update case where a tag match happens, we update the value of this table entry because the observed run length may have potentially changed. We encode I/O event frequency to discrete state value that RLE predictor can use at a precision of 50 times/100ms(for example, a frequency of 125 times/ms will be encoded to *state 3*) and select a temporal granularity of 100ms as sampling period. We experimentally verified that this configuration provided the best trade-off between sensitivity of state variation and predictor efficiency.

# *B. Execution phase tracking and VM dynamic migration*

With the prediction result of I/O intensity, we could further track different execution phases of applications and then decide whether a scheduling adjustment should be performed to optimize the execution of program in the coming period. In our design, we expect to schedule VMs on I/O cpupool only when they are in heaviest I/O load state to maximize the benefit of I/O scheduling optimization. To achieve this, we need to specify a proper threshold to differentiate heavy and low I/O load state and setup a proper condition for VM migration.

**I/O load intensity threshold**: This threshold is used to estimate whether a VM will enter heavy I/O load state and should be scheduled with I/O-oriented optimization. As the I/O behavior of different applications have significantly distinction and their load intensity could vary over time, static threshold would be inappropriate. Since the purpose of our scheduling optimization is to maximize the benefit of I/O scheduling while limit the negative influence of VM migration, this threshold should be able to maximize the I/O load intensity difference between different execution phases. For this purpose, we borrowed an idea of segmentation from digital image processing. Image segmentation is used to distinguish objects from background based on their characteristic difference which is always gray scale. In our study, transient execution phases with noticeable I/O intensity variations could also be considered as isolated objects that spread across the whole execution process which could be considered as the background. The distinction is that the characteristic difference is reflected by I/O load intensity rather than gray value in digital image processing.

In this paper, we applied classic OTSU (Maximization of interclass variance) algorithm [15] to obtain a dynamic threshold. This algorithm attempts to get an optimum threshold through searching the maximal interclass variance in a digital image based on its histogram and probability of pixel gray value. Compare to other common-used segmentation algorithms such as adaptive iteration and morphology method, OTSU algorithm has better adaptability and got best results for most of our study cases. In this paper, we replace the gray value of pixels by I/O event frequency and calculate the interclass variance based on the histogram of I/O intensity history. The revised OTSU algorithm applied here can be formulated as follow:

Let the samples of a given I/O intensity history be represented in m intensity levels [1, 2, 3... m]. The number of samples at level i can be denoted by ni. And total number of samples:

$$N=\sum_{1}^{m}n_{i}.$$

Probability distribution of different I/O intensity levels:

$$P_{i}=n_{i}/N$$

Separate history samples into two classes C0 = (1 ∼ k) and C1 = (k + 1 ∼ m) which represent background and objects respectively (low and heavy I/O execution phases in our study) by a threshold k. In this case, the probabilities of class occurrence of C0 and C1 are given by:

$$\begin{array}{c}{{\xi_{0}=\sum\limits_{i=1}^{k}P_{i}=\omega_{k}}}\\ {{\xi_{1}=\sum\limits_{i=k+1}^{m}P_{i}=1-\omega_{k}}}\end{array}$$

and the class mean values of C0 and C1 are given by:

$$\begin{array}{c}{{\mu_{0}=\sum\limits_{i=1}^{k}\{i P_{i}/\xi_{0}\}=\mu_{k}/\omega_{k}}}\\ {{\mu_{1}=\sum\limits_{i=k+1}^{m}\{i P_{i}/\xi_{1}\}=(\mu-\mu_{k})/(1-\omega_{k})}}\end{array}$$

where

$$\mu_{k}=\sum_{i=1}^{k}i P_{i}$$

The total mean value of I/O intensity history is:

$$\mu=\sum_{i=1}^{m}i P_{i}=\xi_{0}\mu_{0}+\xi_{1}\mu_{1},$$

and we can easily verify the following relation for any choice of k:

$$\xi_{0}+\xi_{1}=1$$

Finally, the interclass variance $\sigma_{k}^{2}$ are given by:

$\sigma_{k}^{2}=\xi_{0}(\mu_{0}-\mu)^{2}+\xi_{1}(\mu_{1}-\mu)^{2}=\xi_{0}\xi_{1}(\mu_{1}-\mu_{0})^{2}$

$(\omega_{k}\mu-\mu_{k})^{2}/[\omega_{k}(1-\omega_{k})]$

2 =

We iterate threshold k from 1 to m and find the result which can maximize the interclass variance σ2 k.

(ωkμ − μk)

An important factor affecting the threshold calculation is history size. Larger history size could better reflect the entire characteristic of program while a smaller one could detect more variation detail. We compared the effect of different configurations and finally set it to 200 because this temporal length has been able to cover several complete iteration periods for most of our study cases while avoid inducing too much noisy which could lead to unnecessary phase transition. We update the threshold each 50 sampling periods to perceive the possible variation of entire I/O load state. We applied this algorithm to our study cases and got ideal result. For samples of LU, SP and CG programs in Figure 2, the I/O intensity thresholds are 97, 69 and 247 respectively. These results have been able to distinguish transient execution phases from stable execution process clearly.

**VM migration condition**: After calculating the threshold of I/O intensity, we also need to set a condition to decide whether a VM migration should be performed immediately to adapt to the predicted variation of I/O load state in the coming period. In this paper, we apply a weaker condition for migrating VM to I/O cpupool and a stricter condition for reverse operation. Each time a VM's prediction result exceeds the I/O intensity threshold, we will migrate it to the I/O cpupool instantly. However, a VM will be migrated back to the computing cpupool only when its practical I/O intensity is lower than the threshold in three continuous periods and its I/O prediction result of coming period is also under the threshold. This configuration makes sure that heavy I/O execution phases could always be perceived and optimized in the first place although computing performance could suffer from I/O scheduling. We experimentally compared the performance degradations caused by communication latency increasing and scheduling computing jobs on I/O cpupool. We found the former one was much worse especially for those communication-intensive applications(eg. the performance of CG program reduced more than 40% when average network latency increases from 0.5ms to 10ms). Therefore, we think strict exit condition for I/O-intensive execution phase should be a rational choice for our study.

In summary, we divide the entire execution process of applications into different phases with the I/O intensity threshold and VM migration condition. This dynamic dividing isolates the execution of I/O and computing jobs with finer temporal granularity and thus reduces the performance interference caused by scheduling competition.

# *C. Cooperative scheduling based on VMs grouping*

During our test, we found there was strong correlation between the I/O behaviors of multiple virtual machines which cooperate together to perform the same parallel program. In this section, we will describe how to use this correlation to further optimize the VM scheduling.

**Grouping migration**: Cooperative virtual machines undertake different processes of the same parallel program and they usually communicate with each other periodically to synchronize computing result or data. However, serious CPU competition and disordered VM scheduling could prevent inter-VM communication finishing in time and then cause serious synchronization latency or timeout. Currently, some scholars have proved that the co-scheduling approach is an efficient way to address the inter-process synchronization issue under virtualized environment [16]. Therefore, in this study, we also applied similar mechanism to optimize the migration strategy of multiple cooperative virtual machines. As illustrated in Figure 3, we congregate several VMs into the same group if they have cooperation relationship (E.g. four VMs running LU program will be put into the same group while four VMs running CG program will be put into another). VMs belong to the same group will always be migrated between different cpupools concurrently. This mechanism guarantees that all cooperative VMs could always benefit from I/O scheduling simultaneously when they are both in I/O-intensive load state and thus maximizes the efficiency of inter-VM communication. It also reduces the possibility that one virtual machine becomes the bottleneck of entire group because of its own scheduling delay.

**Cpupool topology optimization**: Besides VM migration strategy, across-VM correlation also influences the topology of cpupool allocation. Currently, virtual network drivers prefer to apply memory sharing mechanism to speed up the network communication between multiple virtual machines which deployed in the same physical platform. In this case, the capacity of data transmission could get noticeable promotion if shared cache can be efficiently utilized. In our design, we try to deploy I/O and computing cpupools into individual processor sockets to make sure cooperative VMs could take fully advantage of cache sharing when performing inter-VM communication. Although this isolation between I/O and computing cpupools could increase the cost of VM migration because of cache flushing, this overhead can be efficiently controlled since we have limited the frequency of VM migration through accurate I/O intensity threshold and strict VM migration condition setting.

It needs to point out that we only group virtual machines statically in this study. This needs users to provide grouping information explicitly before VMs are deployed into system. However, sometimes sever provider might not be able to get this information from customers or users could change their application deployment during system running. In this case, some automatic recognizing mechanisms would be necessary to detect the cooperation relationship between multiple virtual machines. Although we haven't further investigated this issue in this paper, we believe some simple pattern identification methods based on I/O behavior characterizing, such as periodicity comparison or correlation analysis would be sufficient to address this problem.

## IV. SYSTEM IMPLEMENTATION

4.0 and earlier versions of Xen virtual machine system employed traditional global-symmetric scheduler to manage VMs. Both of the main scheduler framework and specific scheduling algorithm need to be modified to realize the asymmetric scheduling. Currently, the latest Xen-4.1 system provides a CPUPOOL feature which allows several individual cpu subsets coexist in the system. Each cpupool has specific quantity of CPU resources which are managed by its own scheduler and virtual machines can be migrated across different cpupools easily. Although only Credit scheduler completely supports the CPUPOOL mechanism currently, most important management functions have been realized in Xen-4.1.0 system, including cpupool creating and destroying, processor resource adding and removing, VM migrating and etc. Based on this framework, asymmetric scheduling can be achieved in a more modular and graceful way.

As illustrated in Figure 3, we increase a round-robin(RR) scheduler to Xen virtual machine and use it to manage a

![](_page_7_Figure_0.png)

Figure 4. Total running time of NPB benchmarks

 

specific *I/O cpupool*. This scheduler applies frequent context switch to speed up I/O operations and schedules VMs in order according to their sequence in scheduling queue. Beside I/O cpupool, there is another *computing cpupool* which applies default Xen-Credit scheduler to undertake VMs that perform less I/O operations. During system running, we trace the I/O load states of each virtual machine dynamically and consider to migrate them between I/O and computing cpupools if we predict their I/O load intensity will significantly change.

## V. EXPERIMENT AND EVALUATION

In order to estimate the functionality and efficiency of our scheduling model, we performed several experiments based on our prototype system to test both of the entire performance promotion and the overhead caused by VM dynamic migration. As the test in section II, we also ran four VMs in a single platform to execute NPB benchmarks with four parallel processes. Our test covered three different cases: 1)Four VMs share two process cores that managed by default Credit scheduler; 2)Four VMs share two processor cores that managed by simple round-robin scheduler with scheduling period of 0.5ms; 3) VMs are dynamic migrated based on the principle described in section III between I/O and computing cpupools which both have two processor cores. During this test, we just deployed I/O and computing cpupools statically in an Intel Q9550 quadcore processor. Although resource and load balance between I/O and computing cpupools is an important issue that we will exploited, we don't want to induce this factor to current test. We hope this result could just reflect the effect of dynamic scheduling based on I/O behavior tracking clearly. At the same time, we also didn't treat the driver domain(domain0) specially since its CPU usage was always very low during our test and thus caused little effect to the result. We compare the performance of five NPB programs with different scheduling configurations with total running time and Mfops and test results are illustrated in Figure 4 and Table IV.

As illustrated in Figure 4, the performance of both BT, LU, EP and SP programs got growth of different levels compared to the case using simple RR scheduler. The total mops of BT and SP increased about 13.5% and 10.9% respectively while the one of LU increased about 14.6%.

Table IV TOTAL MOPS OF NPB BENCHMARKS BT CG EP LU SP Credit 1295.52 148.18 36.3 716.46 394.99 SimpleRR 1709.23 288.53 32.33 878.28 543.62 AsymSched 1884.34 268.75 36.48 982.90 586.79

This promotion was mainly caused by the dynamic VM migration strategy which partly effaced the overhead caused by scheduling computing jobs with frequent context switch and thus protected the efficiency of system. Compared to aforementioned three programs, the performance variation of EP program could exhibit this problem more clearly. Since EP program has a pseudo parallel kernel which virtually requires no inter-processor communication during its execution, it suffered performance degradation that mainly caused by frequent context switch when being performed using simple RR scheduler. With our scheduling model, this program will be treated as a simple computing job and be scheduled in computing cpupool during its entire execution. Therefore, it achieved similar performance as the case using default Xen-Credit scheduler.

However, different from other programs, the performance of CG program reduced about 6.8% after using our scheduling strategy. In order to analyze this unexpected performance degradation, we tracked the VM migration history of CG program. We found sometimes, VMs were migrated back and forth between I/O and computing cpupools in a short duration when periodic low I/O-intensity occurred at the end of each vector multiplication iteration. As illustrated in Figure 5, this phenomenon only happened when low I/O intensity state lasted for more than three continuous sampling periods. As introduced in section II, CG program needs high-intensity network access to perform irregular collective communication during its entire execution. Therefore, its performance gains little benefit from scheduling on computing cpupools while seriously suffered from the VM migrations which not only increased scheduling overhead but also significantly decreased communication efficiency. Therefore, the performance of CG program finally reduced.

Through this test, we proved that the performance of I/O computing mixed HPC programs could get benefit from our dynamic VM migration strategy and the performance improvement significantly depends on the communication mode and I/O behavior characteristic of applications. However, as illustrated in table IV, the performance promotion that benefits from dynamic scheduling is less noticeable than the one from I/O optimization. This result mainly caused by two reasons. First, during our test, we only deployed four virtual computing nodes which configured as a single virtual cluster to undertake the same HPC application. In this case, the negative effects caused by frequent context switch including cache flush and competition was actually minimized because of the data sharing relationship across cooperative virtual machines. In practical use, multiple individual workloads could be deployed into the same platform and thus induce much more overhead when

![](_page_8_Figure_0.png)

 Figure 5. VM migration behavior during CG benchmark execution

 

 scheduling switch frequently happening between multiple unrelated VMs. In this case, our I/O behavior tracking and VM dynamic scheduling approach would be more useful to guarantee the system efficiency. At the same time, we only applied some basic online predictors and algorithms to track the I/O load state of HPC applications. The prediction difference(even more than 30% for some applications as illustrated in Table II and Table III) leads to some irrational scheduling decisions which finally caused unnecessary VM migration operations. This misleading further reduced the efficiency of dynamic scheduling and offset the perform promotion. As illustrated in Figure 4, this negative effect even caused performance degradation rather than promotion when we performed CG program. Therefore, how to promote the accuracy of I/O state predicting and decide the scheduling strategy more properly would be an important prerequisite to further improve our scheduling model.

#### VI. DISCUSSION

# *A. Performance balance between I/O and Computing*

In this study, in order to explain our conception clearly, we just deployed I/O and computing cpupools statically and fairly treated I/O and computing jobs through allocating equal resource to I/O and computing cpupools. However, in practical use, the quantity of I/O-intensive VCPUs could change dynamically since the I/O workload state of each VCPU could vary over time. At the same time, I/O and computing jobs could have significantly different effect to the entire system performance and present complicated correlation which varies over different programming and communication paradigms. In this case, dynamic performance balance between I/O and computing jobs would be necessary to achieve an optimized entire performance. For this issue, some linear or nonlinear programming methodology could help us to decide the optimal resource allocation proportion. However, this optimization might need vast history information and complicated analysis to construct an accurate model and thus not be fit for some practical applications. In this case, pre-analysis based on program design could be helpful to make a correct choice. We will further exploit this issue in our future works.

# *B. VMs cooperation across multiple physical machines*

In section IV, we introduce our methodology of optimizing VM scheduling and cpupool topology by coordinating multiple VMs under single physical platform. However, this optimization could be much more difficult when multiple cooperative VMs are deployed under multiple physical nodes. Since each physical machine could undertake different missions, their workload state might have serious distinction. This state difference could induce uncertainty to both of the scheduling decision and I/O computing balance. Fortunately, most HPC applications have clear and symmetric structure. Therefore, we could deploy multiple cooperative VMs regularly and coordinate their scheduling based on our predesign. Nevertheless, this assumption could be violated under cloud environment since customer could vary their application deployment without notify the service provider. In this case, the system could need to provide predefined interface to customers to get necessary information before optimizing the scheduling scheme. This issue actually refers to resource allocation optimization under cloud computing and we hope our design could provide some inspirations.

## VII. RELATED WORKS

Currently, many scholars have studied the possibility of applying traditional HPC applications into virtualized [4], [5]. They found the poor network communication capacity is the most serious issue that causes performance degradation under virtualized HPC system. Actually, I/O performance regression under virtual machine system has been a widely studied problem and many researches have tried to address this problem from different aspects. E.g., Ongaro [6] et al. explored the impact of a VM scheduler for various combinations of scheduling features over multiple DomUs running different types of applications. Cherkasova *et al.* studied the impact that three different schedulers(BVT, Credit and SEDF) have on the throughput of different I/Ointensive benchmarks [3]. Govindan *et al.* [7] proposed a communication-aware VM scheduling mechanism to improve the performance of high throughput network intensive workloads. And there are many other scholars have tried to optimize the I/O performance of virtual machine from different aspects [17], [18], [19], [20], [8]. However, because of the inherent confliction between I/O and computing, these approach could not overcome the defect of traditional symmetric scheduler and well balance the performance between I/O and communications. Since more and more HPC applications has been deployed into virtulized and cloud environment, resource allocation control at finer granularity and more flexible adaptive scheduler framework become more necessary for future virtualized HPC system design. Therefore, in this paper, we try to analyze the I/O behavior of virtualized HPC applications at fine granularity and propose our conceptions of asymmetric scheduling based on I/O behavior tracking.

# VIII. CONCLUSION

In order to reduce the performance regression caused by communication bottleneck and optimize the scheduling under virtualized HPC system, this paper proposes a dynamic virtual machine scheduling model based on I/O behavior perception and asymmetric scheduling. We promote the performance of inter-VM communication using frequent context switch while isolating the execution of I/O and computing jobs using individual cpupools. At the same time, we also construct a proactive adaptation mechanism based on I/O behavior predicting and dynamic VM migration to achieve a scheduling balance between I/O and computing at fine temporal granularity. We built a prototype system based on Xen-4.1.0 virtual machine and experiment results demonstrate that our approach not only significantly reduces the performance degradation caused by communication latency but also efficiently guarantees the system efficiency through accurate runtime I/O behavior perception and dynamic scheduling.

Currently, more and more traditional HPC applications are consolidated into virtualization and cloud environment to reduce cost and increase flexibility. In this case, how to efface the overhead induced by virtualization layer has become an pivotal basement for entire system design. We hope our work could provide some inspiration for future virtualized HPC system optimization. In future works, we will further complete our design and exploit some other important issues including resource allocation balance between I/O and computing jobs and possible VM scheduling coordination across multiple physical nodes.

# REFERENCES

- [1] Y. Koh, R. Knauerhase, P. Brett, M. Bowman, null Zhihua Wen, and C. Pu, "An analysis of performance interference effects in virtual environments," *IEEE International Symmpo sium on Performance Analysis of Systems and Software*, pp. 200–209, 2007.
- [2] P. Apparao, R. Iyer, X. Zhang, D. Newell, and T. Adelmeyer, "Characterization & analysis of a server consolidation benchmark," in *Proceedings of the fourth ACM SIG- PLAN/SIGOPS international conference on Virtual execution environments(VEE '08)*, 2008, pp. 21–30.
- [3] L. Cherkasova, D. Gupta, and A. Vahdat, "Comparison of the Three CPU Schedulers in Xen," *SIGMETRICS Perform. Eval. Rev.*, vol. 35, no. 2, pp. 42–51, 2007.
- [4] Q. He, S. Zhou, B. Kobler, D. Duffy, and T. McGlynn, "Case study for running hpc applications in public clouds," in *Proceedings of the 19th ACM International Symposium on High Performance Distributed Computing*, ser. HPDC '10, 2010, pp. 395–401.
- [5] J. E. Simons and J. Buell, "Virtualizing high performance computing," *SIGOPS Oper. Syst. Rev.*, vol. 44, pp. 136–145, December 2010.
- [6] D.Ongaro, A. L. Cox, and S. Rixner, "Scheduling I/O in Virtual Machine Monitors," in *Proceedings of the 4th ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'08:)*, Mar. 2008, pp. 1–10.
- [7] S. Govindan, A. R. Nath, A. Das, B. Urgaonkar, and A. Sivasubramaniam, "Xen and Co.: Communication-aware CPU Scheduling for Consolidated Xen-based Hosting Platforms," in *Proceedings of the 3th ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'07)*, June 2007, pp. 126–136.

- [8] H. Kim, H. Lim, J. Jeong, H. Jo, and J. Lee, "Task-aware Virtual Machine Scheduling for I/O Performance," in *Proceedings of the 5th ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'09)*, Mar. 2009, pp. 101–110.
- [9] Y. Hu, X. Long, J. Zhang, J. He, and L. Xia, "I/O Scheduling Model of Virtual Machine Based on Multi-core Dynamic Partitioning," in *Proceedings of the 19th ACM International Symposium on High Performance Distributed Computing*, ser. HPDC '10, 2010.
- [10] "NPB," http://www.nas.nasa.gov/Resources/Software/npb.html.
- [11] H. Jin, M. Frumkin, and J. Yan, "The openmp implementation of nas parallel benchmarks and its performance," Technical Report NAS-99-011, NASA Ames Research Center, Tech. Rep., 1999.
- [12] E. Duesterwald, C. Cascaval, and S. Dwarkadas, "Characterizing and predicting program behavior and its variability," in *Proceedings of the 12th International Conference on Parallel Architectures and Compilation Techniques*, ser. PACT '03.
- [13] A. S. Dhodapkar and J. E. Smith, "Managing Multiconfigu ration Hardware via Dynamic Working Set Analysis," in *Proceedings of the 29th International Symposium on Computer Architecture, ISCA-29*, May 2002.
- [14] S. S. T. Sherwood and B. Calder, "Phase Tracking and Pre diction," in *Proceedings of the 30th International Symposium on Computer Architecture, ISCA-30*, June 2003.
- [15] N. OTSU, "A thresholding selection method from gray level histogram," *IEEE Transactions on Systems, Man and Cybernetics*, vol. 9, no. 1, pp. 62 – 66, 1979.
- [16] C. Weng, Z. Wang, M. Li, and X. Lu, "The hybrid scheduling framework for virtual machine systems," in *Proceedings of the 2009 ACM SIGPLAN/SIGOPS international conference on Virtual execution environments*, ser. VEE '09, 2009.
- [17] G. Liao, D. Guo, L. Bhuyan, and S. R. King, "Software Techniques to Improve Virtualized I/O Performance on Multicore Systems," in *Proceedings of the 4th ACM/IEEE Symposium on Architectures for Networking and Communications Systems (ANCS'08)*, Nov. 2008, pp. 161–170.
- [18] K. K. Ram, J. R. Santos, Y. Turner, A. L. Cox, and S. Rixner, "Achieving 10 Gb/s Using Safe and Transparent Network Interface Virtualization," in *Proceedings of the 5th ACM SIG-PLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'09)*, Mar. 2009, pp. 61–70.
- [19] S. R. Seelam and P. J. Teller, "Virtual I/O Scheduler: a Scheduler of Schedulers for Performance Virtualization," in *Proceedings of the 3th ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'07)*, June 2007, pp. 105–115.
- [20] A. .Menon, A. L. Cox, and W. Zwaenepoel, "Optimizing Network Virtualization in Xen," in *Proceedings of the USENIX 2006 Annual Technical Conference (USENIX'06)*. Berkeley, CA, USA: USENIX Association, June 2006, pp. 2–2.

