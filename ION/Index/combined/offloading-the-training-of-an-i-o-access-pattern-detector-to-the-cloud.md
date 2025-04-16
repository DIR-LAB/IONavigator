PADW)

# Offloading the Training of an I/O Access Pattern Detector to the Cloud

Cristiano A. Kunas ¨ , Matheus S. Serpa1 , Jean Luca Bez3 , Edson L. Padoin2 , Philippe O. A. Navaux1 Institute of Informatics, Federal University of Rio Grande do Sul (UFRGS) — Porto Alegre, Brazil Regional University of Northwestern Rio Grande do Sul (UNIJU´I) — Iju´ı, Brazil

3Lawrence Berkeley National Laboratory — Berkeley, USA

{cakunas, msserpa, navaux}@inf.ufrgs.br, jlbez@lbl.gov, padoin@unijui.edu.br

*Abstract*—I/O operations are a bottleneck for numerous applications, so optimizing the performance of these operations is of paramount importance. Many techniques explore and apply optimizations to different layers of the I/O stack to improve performance. The difficulty that arises is that the workload changes constantly. So detecting access patterns correctly, at runtime, becomes essential for systems that seek to self-adjust their parameters. Furthermore, the I/O pattern detection techniques should represent minimal overhead and should be able to perform detection as quickly as possible. This paper approaches a machine learning technique for detecting the I/O access patterns and proposes offloading the local training workload to the cloud using a TPU accelerator. Such an approach does not interfere with classifier accuracy (reaching up to 99% accuracy). Still, it allows the training to be asynchronous, enabling the local machine to allocate its computing resources to scientific applications while the model is trained or updated in the cloud.

*Index Terms*—high-performance computing; access pattern detection; classification; TPU; cloud;

#### I. INTRODUCTION

In the context of HPC, applications issue their input and output (I/O) operation to a shared Parallel File System (PFS), where dedicated machines act as data servers [1], [2]. These I/O operations are often considered a bottleneck for a growing set of applications. Furthermore, numerous factors can impact their performance, such as the deployment and configuration of the shared storage infrastructure, network topology to accessing PFS servers, the set of libraries used, and their access pattern. This last factor is the target of many optimization techniques as it defines how the applications issue their I/O requests, i.e., the operation (writes or read), spatiality (contiguous, 1D-strided, or random), and size of the requests [3].

The optimization techniques, which seek to improve performance by reshaping the applications' I/O access patterns, include aggregation, request reordering, collective operations, and scheduling [4], [5], [6], [7]. These techniques can be applied at different layers of the I/O stack and commonly improve the I/O performance for specific system settings and access patterns, but not for all of them. Hence, achieving the best results proposed by these techniques often relies on accurately tunning them to the current I/O workload. However, the constant change of observed patterns as new applications start and finish their I/O phases adds additional challenges. Consequently, it is vital for systems seeking to self-adjust their parameters to detect the access patterns correctly and efficiently at runtime.

As mentioned, any runtime detection technique should pose minimal overhead to be used in large-scale systems. These mechanisms should detect the current pattern as quickly as possible to allow tuning mechanisms and optimization techniques to act on the information, enabling the system to benefit from good choices. In this scenario, we can consider applying machine learning techniques that can automatically detect the I/O access pattern of HPC applications at runtime. Even though the training phases can be expensive, once the model has learned its parameters, inference on previously unseen data is fast to be used in runtime, as demonstrated by Bez et al.[8].

In this paper, we propose offloading the model training by using the cloud. Thus, we avoid further burdening the system, which is already highly overloaded by the plethora of running applications. To do this, we adapted the neural network model implemented in [8] to enable training on Tensor Processing Unit (TPU) devices. We demonstrate such an approach to be promising, considering that in a production environment, the number of observations collected to (re)train the model will be much larger than what we used in our experiments.

The rest of this paper is organized as follows. Section II discusses work related to access pattern detection. We detailed the approach used to detect access patterns in Section III, and the processing architectures. Section IV presents the evaluation results covering accuracy and performance. Section V concludes the paper and points to future work.

## II. RELATED WORK

Access pattern detection is a critical part of the optimization problem, as it allows you to adapt the I/O system to the observed workload correctly. For this, postmortem and runtime approaches can be adopted. For postmortem, information is obtained from traces and applied to future runs of the same applications [9], [10], targeting repeated patterns with similar characteristics. On the other hand, this paper focuses on a runtime technique to avoid imposing the profiling effort but also to benefit from the similarities between different applications. A strength of runtime detection is that it allows applications to start profiting from tuning optimizations faster.

<sup>978-1-6654-1730-3/21/$31.00 ©2021</sup> IEEE

DOI 10.1109/SBAC-PADW53941.2021.00013 Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:54:44 UTC from IEEE Xplore. Restrictions apply.

At runtime, techniques can usually only use information from operations that have already been issued. Trying to predict when future I/O operations will happen, where and how much data will be accessed, Dorier et al. [11] proposed Omnisc'IO. It intercepts I/O operations and builds a grammarbased model of the I/O behavior of applications. It works without prior knowledge of the application and converges to accurate predictions with just a few iterations. The approach employed by Tang et al. [12] periodically analyzes previous accesses and applies a library of rules to predict future accesses (for prefetching) in an online analyzer capable of detecting structured and unstructured patterns. They collect metrics about the spatiality of read requests from the MPI-IO library. The overall runtime reduction is up to 26% via pattern-aware prefetching with an accuracy of up to 99%.

Other techniques benefit from information obtained from high-level I/O libraries. Ge et al. [13] presented a parallel I/O middleware approach based on MPI-IO to enable energy consciousness for I/O intensive applications. This approach combines runtime I/O access interception and Dynamic Voltage and Frequency Scaling (DVFS) capability available on modern processors to schedule the system's power-performance mode for energy savings intelligently. They collect data from MPI-IO covering the type of operation, data size, spatiality, and whether or not the operations are collective and synchronous. Experimental evaluations demonstrated that such an approach could reduce system energy by 9% to 28% without decreasing application performance by correctly identifying the application's I/O behavior.

We also briefly cover some examples where access pattern detection is used to guide different optimization and tuning techniques. For instance, Song et al. [14] used the spatiality of I/O requests to build a cost-intelligent data access strategy seeking to increase the performance of parallel file systems. They present a novel model to estimate the data access cost of different data layout policies and extended that cost model to calculate the overall I/O cost of the applications and choose an appropriate layout policy for each application. Experimental results show that the approach achieved up to 74% performance improvement for data-intensive applications.

## III. NEURAL NETWORK ACCESS PATTERN DETECTION

In this section, we describe the Neural Network model that we propose to offload to the cloud. Once trained, it can be used to detect the I/O access pattern of HPC applications at runtime. The dataset used to train this model contains metrics collected at runtime on access patterns frequently used by the HPC I/O community (they cover ≈ 39,000 observations). The patterns are classified according to the file approach (single file vs. file-per-process) and the spatiality (contiguous or 1Dstrided) into three classes. We do not consider the 1D-strided approach for the file-per-process as it is not representative. The dataset is public and available in the companion repository at cristianokunas.gitlab.io/wcc-sbac-pad-2021.

The first class is the file-per-process with contiguous access (Fig. 1(a)), where each process of an application issues

![](_page_1_Figure_6.png)

(c) Shared file with with 1D-strided accesses

Fig. 1. Visual representation of three different I/O access patterns commonly observed in scientific HPC applications.

its operations in its own file accessing one offset after the other. The second class is the shared file with contiguous access (Fig. 1(b)), where all the processes read and write data to a common file by accessing contiguous chunks of the file. Finally, the third class is the shared file with 1D-strided access (Fig. 1(c)) where each process accesses portions of the file with a fixed-size gap between them.

This model was initially proposed to work at the I/O forwarding layer of HPC systems (though not restricted to it). Its access pattern detection engine receives input information collected at each I/O node, which stands between the compute nodes and the PFS. This information, referring to the previous observation period, consists of the request size (minimum, average, maximum), the number of file identifiers, and the average distance between consecutive requests for the same file identifier (to represent the spatiality of accesses). The authors selected these parameters after applying the Spearman non-parametric correlation [15] to identify those most related to the access pattern class.

## *A. The Neural Network Architecture*

The classifier implementation uses Keras [16], a high-level neural network API with TensorFlow [17] as the back-end. Before feeding the metrics to the Neural Network, we applied Yeo-Johnson [18], scaling, and data transformations to make the data more suitable for the network and to speed up training. Yeo-Johnson is a power-transform similar to Box-Cox [19], but that supports zero or negative value features. In this particular case, some metrics can have zero values. The scale transformation calculates the standard deviation for a characteristic and divides each value by that deviation. Finally, the data transform computes the mean and subtracts it from each value.

The model is built with three layers, as illustrated in Fig. 2: an input layer with all five features (metrics), a hidden layer with the same number of neurons, and an output layer with three units, one to represent each access pattern class. The first two layers use a Rectified Linear Unit (ReLU) [20] activation function with a normal kernel initialization function. The ReLU activation introduces non-linearity into the network. The output layer uses a *softmax* activation function to crunch the outputs of each unit in the range [0, 1] and ensure that the sum of the outputs equals 1.

![](_page_2_Figure_2.png)

Fig. 2. Neural network architecture to classify metrics into three classes, regarding file layout and access spatiality [8].

The model uses the optimizer RMSProp, with a learning rate of 0.001 and momentum of 0.9. The loss function was *categorical cross-entropy*. The result has an n-dimensional vector that is all-zeros except for a one at the index corresponding to the sample class. In our case, we have a three-dimensional vector for each sample. We have followed the same approach used in previous work, where we split the dataset in two using Scikit-Learn [21]: 70% for training and 30% for testing.

## *B. The Google Cloud TPU*

In this section, we introduce Google's TPU architecture, used in our experiments. TPUs are application-specific integrated circuits (ASICs). Fig. 3 shows the architecture of a TPUv2 chip. Each TPUv2 device has four internal chips, and each is made up of two cores. Each core has scalar, vector, and matrix units (MXU) connected with the on-chip high bandwidth memory (HBM) of the 8 GB for each TPUv2 core. The performance of each TPU chip is 180 TFlops (32 bit and 16-bit mixed precision) [22]. Compared to TPUv2, TPUv3 doubles the number of MXUs and HBM capacity per core and has a peak of 420 TFlops, 2.3× greater than TPUv2 [23]. Furthermore, each core of the TPU device performs calculations independently, and the high bandwidth interconnections allow the chips to communicate directly with each other in the TPU device [24].

![](_page_2_Figure_8.png)

Fig. 3. The architecture of TPUv2 that can achieve up to 180 Tflops.

Fig. 4 illustrates how a user can get access to a Cloud TPU. Cloud TPUs are network-attached. The user needs to create a compute engine virtual machine and apply a cloud TPU. The virtual machine connects to the cloud TPU through grpc1 , a Google's open-source high-performance Remote Procedure Call that can run in any environment. Users do not need to install any driver and can just use the machine images provided by Google Cloud. However, the users still need to design the algorithm and write the code for their own applications [22].

![](_page_2_Figure_11.png)

Fig. 4. Illustration on how to offload to a cloud TPU.

Configuring the Cloud TPU model requires a strategy to allow distributed training across all cores. This strategy scales the batch size by the number of available TPU chips, i.e., if the batch size is 32, the global batch will be 256 (8 × 32 = 256). The global batch size is fragmented automatically across all replicas [25].

## *C. Experimental Platforms*

The experiments described in this paper were conducted on the computational resources available at the Google Cloud 2 , in the PCAD infrastructure at INF/UFRGS 3 , and Santos Dumont Supercomputer (SDumont) 4 at the National Laboratory for Scientific Computing (LNCC):

https://grpc.io/ https://cloud.google.com/ http://gppd-hpc.inf.ufrgs.br/ https://sdumont.lncc.br

*1) Cloud TPUv2:* We use a single TPUv2 with 8 cores and 64 GB memory. The TPU device provides 180 Teraflops performance. This environment is named TPUv2 throughout the rest of this paper.

*2) Cloud TPUv3:* We use a single TPUv3 with 8 cores and 128 GB memory. The TPU device provides 420 Teraflops performance. This environment is named TPUv3 throughout the rest of this paper.

*3) Blaise:* A single compute node composed of two Intel Xeon E5-2699 v4 Broadwell (2.2GHz) CPU, 44 physical cores (22 per socket), 256 GB of RAM, and four NVIDIA Tesla P100-SXM2-16GB. All the experiments conducted used only one GPU. This environment is named P100 throughout the rest of this paper.

*4) Bull Sequana X1120 (GPU):* A single compute node composed of two Intel Xeon Cascade Lake Gold 6252 (2.1GHz) CPU, 48 physical cores (24 per socket), 384 GB of RAM, and four NVIDIA Tesla V100-SXM2-32GB. All the experiments conducted also used only one GPU. This environment is named V100 throughout the rest of this paper.

## IV. ACCURACY AND PERFORMANCE ANALYSIS

This section compares the accuracy and performance metrics collected from ten executions of the Neural Network I/O access pattern detection model on the P100, TPUv2, V100, and TPUv3. The Kolmogorov-Smirnov [26] test was applied to all results, and they did not rule out a normal distribution. Therefore, all values shown are averages and the t-test [27] is used to compare them. We trained the model on 27,238 samples and tested it on 11,674 samples, with a batch size of 32 and limiting to 50 epochs. It is important to notice that all three classes are correctly identified with reasonable probability. The model's accuracy exceeds 99% for training and testing, with a standard deviation of less than 1%. The statistical test has indicated that the training accuracy is not significantly different, but the testing accuracy is significantly different. Fig. 5 depicts the accuracy when running in each platform.

![](_page_3_Figure_6.png)

Fig. 5. Training and testing accuracy of the Neural Network model.

The performance metrics are illustrated in Fig. 6. The t-test was used to compare all sets of time metrics collected and indicates that the results of training times are significantly different from each other. The average training time on the V100 was ≈ 1.74× faster than on the P100, and the mean training time of TPUv2 was ≈ 1.41× faster than on the P100. However, using the V100, we observed a speedup of ≈ 1.24× compared to the TPUv2. On the other hand, the average training time on the TPUv3 was ≈ 1.68× faster than on the P100, and ≈ 1.20× faster than on the TPUv2. But, the speedup observed on the V100 over the TPUv2 is not observed compared to the TPUv3. The V100 was only ≈ 1.03× faster than on the TPUv3. The first hypothesis to explain this result is that the application context may negatively influence performance since it is a relatively small model with few parameters. The second point is that TPUs can perform better when the batch size is larger, making better use of TPU memory. The documentation recommends that to optimize memory use, you should use the largest batch size that can fit in memory.

![](_page_3_Figure_9.png)

Fig. 6. Training and testing times of the Neural Network in each hardware.

The experimental results indicate that Cloud TPU can be a good choice for training the I/O access pattern detector. Although there may be a cost related to transferring the dataset to the cloud (we measured it to be ≈ 2 seconds for our dataset), it is offset by the training time. Furthermore, it also prevents introducing more concurrence to local resources. It is important to note that, in a production environment, the number of observations collected to (re)train the model will be more expressive, which may cause a more significant burden on the HPC system, as the dataset gets larger.

## V. CONCLUSION AND FUTURE WORK

In this paper, we sought to evaluate the accuracy and performance of training the I/O access pattern classifier by

18

asynchronously offloading the training to the cloud using TPU devices. Such an approach aids in alleviating the contention for high-demanded local HPC resources, allowing them to be focused on running applications.

The model presented accuracy above 99% for the training and test datasets in the three computing environments we explored. The average training time of the model on TPUv2 was ≈ 1.41× faster than on P100. The performance of V100 was ≈ ×1.24 faster than on TPUv2. Training the model on cloud TPU devices is feasible because the (re)training phase can take longer to complete and can be done asynchronously in the background.

Future work will extend the performance evaluation to different Cloud TPUs, varying the version and the number of cores, such as TPUv2-32 and TPUv3-32. In addition, we plan to extend the dataset and evaluate the impact of batch size on training since they are designed for large batch sizes and workloads.

## ACKNOWLEDGMENT

This work has been partially supported by Petrobras (2016/00133-9, 2018/00263-5) and Green Cloud project (2016/2551-0000 488-9), from FAPERGS and CNPq Brazil, program PRONEX 12/2014 and MCTIC/CNPq - Universal 28/2018 under grants 436339/2018-8. This study was financed in part by the Coordenac¸ao de Aperfeic¸oamento de Pes- ˜ soal de N´ıvel Superior – Brasil (CAPES) – Finance Code 001. Some experiments in this work used the PCAD infrastructure, http://gppd-hpc.inf.ufrgs.br, at INF/UFRGS. The authors acknowledge the National Laboratory for Scientific Computing (LNCC/MCTI, Brazil) for providing HPC resources of the SDumont supercomputer, which have contributed to the research results reported within this paper. URL: http://sdumont.lncc.br. This research has used resources from the U.S. Department of Energy Office of Science User Facility located at Lawrence Berkeley National Laboratory, operated under Contract No. DE-AC02-05CH11231.

#### REFERENCES

- [1] R. B. Ross, R. Thakur *et al.*, "Pvfs: A parallel file system for linux clusters," in *Proceedings of the 4th annual Linux showcase and conference*, 2000, pp. 391–430.
- [2] S. Microsystem, "Lustre file system: High-performance storage architecture and scalable cluster file system," *Sun Microsystem White Paper*, 2007.
- [3] F. Z. Boito, E. C. Inacio, J. L. Bez, P. O. Navaux, M. A. Dantas, and Y. Denneulin, "A checkpoint of research on parallel i/o for highperformance computing," *ACM Computing Surveys (CSUR)*, vol. 51, no. 2, pp. 1–35, 2018.
- [4] S. Kumar, A. Saha, V. Vishwanath, P. Carns, J. A. Schmidt, G. Scorzelli, H. Kolla, R. Grout, R. Latham, R. Ross *et al.*, "Characterization and modeling of pidx parallel i/o for performance optimization," in *Proceedings of the International Conference on High Performance Computing, Networking, Storage and Analysis*, 2013, pp. 1–12.
- [5] Z. Wang, X. Shi, H. Jin, S. Wu, and Y. Chen, "Iteration based collective i/o strategy for parallel i/o systems," in *2014 14th IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing*. IEEE, 2014, pp. 287–294.
- [6] G. Congiu, S. Narasimhamurthy, T. Suß, and A. Brinkmann, "Improving ¨ collective i/o performance using non-volatile memory devices," in *2016 IEEE International Conference on Cluster Computing (CLUSTER)*. IEEE, 2016, pp. 120–129.

- [7] F. Tessier, V. Vishwanath, and E. Jeannot, "Tapioca: An i/o library for optimized topology-aware data aggregation on large-scale supercomputers," in *2017 IEEE International Conference on Cluster Computing (CLUSTER)*. IEEE, 2017, pp. 70–80.
- [8] J. L. Bez, F. Z. Boito, R. Nou, A. Miranda, T. Cortes, and P. O. A. Navaux, "Detecting i/o access patterns of hpc workloads at runtime," in *2019 31st International Symposium on Computer Architecture and High Performance Computing (SBAC-PAD)*, 2019, pp. 80–87.
- [9] F. Z. Boito, R. V. Kassick, P. O. Navaux, and Y. Denneulin, "Automatic i/o scheduling algorithm selection for parallel file systems," *Concurrency and Computation: Practice and Experience*, vol. 28, no. 8, pp. 2457– 2472, 2016.
- [10] Y. Liu, R. Gunasekaran, X. Ma, and S. S. Vazhkudai, "Automatic identification of application i/o signatures from noisy server-side traces," in *12th* {*USENIX*} *Conference on File and Storage Technologies (*{*FAST*} 14), 2014, pp. 213–228.
- [11] M. Dorier, S. Ibrahim, G. Antoniu, and R. Ross, "Omnisc'io: a grammarbased approach to spatial and temporal i/o patterns prediction," in *SC'14: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*. IEEE, 2014, pp. 623– 634.
- [12] H. Tang, X. Zou, J. Jenkins, D. A. Boyuka, S. Ranshous, D. Kimpe, S. Klasky, and N. F. Samatova, "Improving read performance with online access pattern analysis and prefetching," in *European Conference on Parallel Processing*. Springer, 2014, pp. 246–257.
- [13] R. Ge, X. Feng, and X.-H. Sun, "Sera-io: Integrating energy consciousness into parallel i/o middleware," in *2012 12th IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing (ccgrid 2012)*. IEEE, 2012, pp. 204–211.
- [14] H. Song, Y. Yin, Y. Chen, and X.-H. Sun, "A cost-intelligent applicationspecific data layout scheme for parallel file systems," in *Proceedings of the 20th international symposium on High performance distributed computing*, 2011, pp. 37–48.
- [15] C. Spearman, "The proof and measurement of association between two things." *The American Journal of Psychology*, vol. 15, pp. 72–101, 1904.
- [16] J. Moolayil, "An introduction to deep learning and keras," in *Learn Keras for Deep Neural Networks*. Springer, 2019, pp. 1–16.
- [17] M. Abadi, A. Agarwal, P. Barham, E. Brevdo, Z. Chen, C. Citro, G. S. Corrado, A. Davis, J. Dean, M. Devin *et al.*, "Tensorflow: Large-scale machine learning on heterogeneous distributed systems," *arXiv preprint arXiv:1603.04467*, 2016.
- [18] I.-K. Yeo and R. A. Johnson, "A new family of power transformations to improve normality or symmetry," *Biometrika*, vol. 87, no. 4, pp. 954– 959, 2000.
- [19] G. E. Box and D. R. Cox, "An analysis of transformations," *Journal of the Royal Statistical Society: Series B (Methodological)*, vol. 26, no. 2, pp. 211–243, 1964.
- [20] R. H. Hahnloser, R. Sarpeshkar, M. A. Mahowald, R. J. Douglas, and H. S. Seung, "Digital selection and analogue amplification coexist in a cortex-inspired silicon circuit," *Nature*, vol. 405, no. 6789, pp. 947–951, 2000.
- [21] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg *et al.*, "Scikit-learn: Machine learning in python," *the Journal of machine Learning research*, vol. 12, pp. 2825–2830, 2011.
- [22] Y. You, Z. Zhang, C.-J. Hsieh, J. Demmel, and K. Keutzer, "Fast deep neural network training on distributed systems and cloud tpus," *IEEE Transactions on Parallel and Distributed Systems*, vol. 30, no. 11, pp. 2449–2462, 2019.
- [23] Y. E. Wang, G.-Y. Wei, and D. Brooks, "Benchmarking tpu, gpu, and cpu platforms for deep learning," *arXiv preprint arXiv:1907.10701*, 2019.
- [24] Google. (2021) Cloud tpu system architecture. [Accessed Aug. 20, 2021]. [Online]. Available: https://cloud.google.com/tpu/docs/ system-architecture-tpu-vm
- [25] ——. (2021) Cloud tpu performance guide. [Accessed Aug. 19, 2021]. [Online]. Available: https://cloud.google.com/tpu/docs/ performance-guide
- [26] H. W. Lilliefors, "On the kolmogorov-smirnov test for normality with mean and variance unknown," *Journal of the American statistical Association*, vol. 62, no. 318, pp. 399–402, 1967.
- [27] T. K. Kim, "T test as a parametric statistic," *Korean journal of anesthesiology*, vol. 68, no. 6, p. 540, 2015.

