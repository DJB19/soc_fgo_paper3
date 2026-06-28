# Evaluation of FGO-Based Battery SOC Estimation Under Aging Conditions Using Public Experimental Datasets

## Abstract

Accurate state-of-charge estimation is a fundamental function of battery management systems for electric vehicles and energy storage applications. In previous simulation-oriented studies, factor graph optimization has shown potential advantages in improving estimation accuracy and robustness by formulating battery state estimation as an optimization problem over model and measurement constraints. However, validation using real experimental battery data remains necessary because practical battery measurements contain non-ideal characteristics such as sensor noise, cycle-to-cycle variation, capacity degradation, and operating condition changes.

This paper evaluates factor graph optimization-based battery SOC estimation under aging conditions using public experimental lithium-ion battery datasets. Different from controlled simulation studies, the proposed evaluation focuses on real discharge cycles obtained from public battery aging experiments. Reference SOC is reconstructed from discharge capacity for selected cycles, and current and voltage measurements are used as input signals for SOC estimation. The performance of FGO is compared with conventional baseline methods, including Coulomb Counting and Kalman-filter-based estimation. Multiple batteries and multiple aging stages are considered to analyze how capacity degradation and cycle variation affect SOC estimation accuracy.

The objective of this study is not to propose a completely new factor graph formulation, but to systematically evaluate the applicability of an FGO-based SOC estimation framework under real experimental aging conditions. Evaluation metrics include root mean square error, mean absolute error, maximum absolute error, and error standard deviation. The results are expected to clarify whether FGO can maintain stable estimation performance across different batteries and aging cycles, and whether it can serve as a reliable state estimation module for future battery monitoring and digital twin applications.

**Keywords**: Battery management system; state-of-charge estimation; factor graph optimization; lithium-ion battery; aging condition; public battery dataset; battery digital twin.

## 1. Introduction

Lithium-ion batteries are widely used in electric vehicles, renewable energy storage systems, portable electronics, and other electrified systems. The performance, safety, and lifetime of these systems depend strongly on the reliability of the battery management system. Among the core functions of a battery management system, state-of-charge estimation is one of the most important tasks because it provides information about the remaining usable capacity of the battery. Accurate SOC estimation is necessary for driving range prediction, charge and discharge control, energy management, and safety protection.

However, SOC cannot be measured directly by a physical sensor. It must be estimated from measurable signals such as current, terminal voltage, and temperature. This estimation problem is challenging because lithium-ion batteries exhibit nonlinear electrochemical behavior, aging-related capacity degradation, temperature dependency, and measurement noise. In addition, the same estimation algorithm may perform differently across different batteries, different cycles, and different aging stages. Therefore, evaluating SOC estimation methods using real experimental battery data is an important step before practical application.

Traditional SOC estimation methods include Coulomb Counting, model-based filtering methods, and data-driven methods. Coulomb Counting estimates SOC by integrating the battery current over time. It is simple and easy to implement, but it is sensitive to initial SOC error, current sensor bias, and capacity uncertainty. Kalman-filter-based methods, such as the Kalman Filter, Extended Kalman Filter, and Unscented Kalman Filter, combine battery models and sensor measurements in a recursive estimation framework. These methods have been widely used in battery management systems because of their computational efficiency. However, their performance depends on the accuracy of the battery model, noise covariance settings, and linearization assumptions.

Factor graph optimization provides another framework for battery state estimation. In a factor graph, the unknown battery states are represented as variable nodes, and the relationships derived from system dynamics and sensor measurements are represented as factor nodes. The estimation problem is formulated as an optimization problem that minimizes the total residual error over the graph. Compared with purely recursive filtering, FGO can naturally incorporate multiple constraints and perform smoothing over a sequence of states. This characteristic makes it potentially useful for battery SOC estimation, especially under noisy measurement conditions.

Our previous study evaluated the robustness of FGO-based SOC estimation using a self-developed C++ battery model under controlled noise conditions. In that study, the noise level and model conditions could be adjusted systematically, which was useful for understanding the basic robustness characteristics of FGO. However, validation using real experimental battery data was still limited. Real battery datasets include measurement noise, capacity degradation, cycle-to-cycle variation, and operating condition changes that cannot be fully represented by a simplified simulation model. Therefore, a more systematic evaluation using public experimental battery datasets is needed.

The present study addresses this limitation by evaluating FGO-based SOC estimation under aging conditions using public lithium-ion battery datasets. The main focus is on discharge cycles because they provide measurable current, voltage, and capacity information that can be used to reconstruct reference SOC. Multiple batteries and multiple aging stages are selected to analyze whether FGO can maintain stable SOC estimation performance as the battery degrades. The proposed evaluation framework compares FGO with conventional baseline methods using quantitative error metrics.

This work is also relevant to future battery digital twin applications. A battery digital twin requires a reliable state estimation module to synchronize the virtual battery model with measured battery data. Although this paper does not construct a complete online battery digital twin system, it evaluates an FGO-based state estimation module that may serve as a core component of future digital twin-based battery monitoring systems.

The main contributions of this paper are summarized as follows:

1. A public experimental dataset-based evaluation framework is established for FGO-based battery SOC estimation under aging conditions.
2. Reference SOC is reconstructed from real discharge cycles, enabling systematic evaluation of SOC estimation accuracy using public battery aging data.
3. The influence of capacity degradation and cycle-to-cycle variation on FGO-based SOC estimation performance is analyzed across selected batteries and aging stages.
4. The performance of FGO is compared with conventional baseline methods, including Coulomb Counting and Kalman-filter-based estimation, using multiple quantitative error metrics.
5. The applicability of FGO as a potential state estimation module for future battery monitoring and digital twin applications is discussed.

The remainder of this paper is organized as follows. Section 2 introduces the public battery dataset and preprocessing procedure. Section 3 describes the SOC estimation methods used in this study, including Coulomb Counting, Kalman-filter-based estimation, and factor graph optimization. Section 4 presents the experimental design and evaluation metrics. Section 5 discusses the results under different aging conditions. Section 6 concludes the paper and outlines future work.


## 2. Public Battery Dataset and Data Preprocessing

### 2.1 Public Battery Aging Dataset

This study uses a public lithium-ion battery aging dataset to evaluate the applicability of factor graph optimization for battery state-of-charge estimation under real experimental conditions. Different from simulation-generated data, public experimental battery datasets contain practical non-ideal characteristics such as measurement noise, capacity degradation, cycle-to-cycle variation, and inconsistent discharge duration. These characteristics are important for evaluating whether a state estimation algorithm can be applied beyond controlled simulation environments.

The primary dataset used in this study is the NASA lithium-ion battery aging dataset. The dataset contains repeated charge, discharge, and impedance measurement profiles for several lithium-ion cells. In this work, the discharge profiles are selected because they provide time-series measurements of current, terminal voltage, temperature, and discharge capacity, which are suitable for SOC reconstruction and estimation evaluation.

In the first stage of this study, battery B0005 is selected as the initial evaluation object. A total of 168 discharge cycles are extracted from the original MATLAB data file. Each discharge cycle contains measured terminal voltage, measured current, measured temperature, time, and cycle capacity. These extracted data are then converted into a unified CSV format for subsequent SOC estimation experiments.

The converted data format includes battery ID, raw cycle index, discharge cycle ID, time, measured terminal voltage, measured current, measured temperature, measured discharge capacity, and reconstructed reference SOC. This unified format allows the same estimation program to be applied to different discharge cycles and, in future extensions, to different batteries in the same dataset.

### 2.2 Discharge Cycle Extraction

The original NASA data file contains different types of operation profiles, including charge, discharge, and impedance measurement. Since this paper focuses on SOC estimation during battery discharge, only discharge cycles are extracted. For each discharge cycle, the following signals are obtained:

\[
t_k,\quad I_k,\quad V_k,\quad T_k,\quad Q_{\mathrm{cycle}}
\]

where \(t_k\) is the time at sample \(k\), \(I_k\) is the measured current, \(V_k\) is the measured terminal voltage, \(T_k\) is the measured temperature, and \(Q_{\mathrm{cycle}}\) is the measured discharge capacity of the corresponding cycle.

The discharge cycles are indexed sequentially after extraction. For battery B0005, 168 discharge cycles are obtained. The early, middle, and late aging stages are represented by selected discharge cycles from the beginning, middle, and end of the extracted cycle sequence. In the initial experiment, cycle 1, cycle 84, and cycle 168 are used as representative cycles for early-stage, middle-stage, and late-stage battery aging, respectively.

This selection strategy allows the influence of battery aging on SOC estimation performance to be analyzed. As the battery ages, the available discharge capacity decreases, and the voltage response may also change. Therefore, comparing estimation performance across different aging stages is useful for evaluating the robustness and practical applicability of the proposed FGO-based SOC estimation framework.

### 2.3 Reference SOC Reconstruction

Since SOC is not directly measured by a physical sensor in the public dataset, a reference SOC trajectory is reconstructed from the discharge capacity of each cycle. At the beginning of each discharge cycle, SOC is assumed to be 1.0, corresponding to a fully charged state. During discharge, the accumulated discharged capacity is calculated by integrating the absolute value of the measured current over time.

The accumulated discharged capacity at sample \(k\) is calculated as:

\[
Q_{\mathrm{dis}}(k)=\sum_{i=1}^{k} |I_i|\Delta t_i
\]

where \(I_i\) is the measured current and \(\Delta t_i\) is the sampling interval between two adjacent measurements, expressed in hours. The reconstructed reference SOC is then defined as:

\[
SOC_{\mathrm{ref}}(k)=1-\frac{Q_{\mathrm{dis}}(k)}{Q_{\mathrm{cycle}}}
\]

where \(Q_{\mathrm{cycle}}\) is the measured discharge capacity of the corresponding cycle.

The reconstructed SOC is clipped to the interval \([0,1]\) to avoid numerical values outside the physically meaningful range caused by measurement noise or numerical integration error. It should be noted that this reference SOC is not a directly measured internal electrochemical state. Instead, it is a capacity-based reference trajectory reconstructed from experimental discharge data. This definition is used as the evaluation reference for comparing different SOC estimation methods.

### 2.4 Capacity Degradation Representation

Battery aging is represented by the degradation of measured discharge capacity over repeated cycles. For each discharge cycle, the corresponding measured capacity is extracted and used to construct a capacity degradation curve. This curve provides a direct representation of the aging process of the selected battery.

For battery B0005, the extracted 168 discharge cycles show a gradual decrease in measured discharge capacity. This capacity degradation is important for SOC estimation because the available capacity appears directly in current-integration-based state transition models. If the capacity value is inaccurate or not updated with aging, SOC estimation error may accumulate.

Therefore, in this paper, capacity degradation is not only treated as a property of the dataset, but also as an important factor influencing SOC estimation performance. The relationship between cycle capacity and SOC estimation error will be analyzed in the experimental section.

### 2.5 Preprocessing Workflow

The complete preprocessing workflow is summarized as follows:

1. Load the original NASA MATLAB battery data file.
2. Extract only discharge cycles from the complete operation profiles.
3. Obtain current, voltage, temperature, time, and measured capacity for each discharge cycle.
4. Reconstruct reference SOC using the accumulated discharged capacity.
5. Save all extracted and reconstructed variables into a unified CSV file.
6. Generate cycle-level summary information, including cycle length, measured capacity, voltage range, and SOC range.
7. Select representative early, middle, and late aging cycles for detailed analysis.

This preprocessing procedure transforms the original public battery dataset into a structured format suitable for FGO-based SOC estimation experiments. It also provides the basis for aging-stage comparison and capacity-error relationship analysis in the following sections.


## 3. SOC Estimation Methods

This section describes the SOC estimation methods used in this study. Three categories of methods are considered: Coulomb Counting, Kalman-filter-based estimation, and factor graph optimization. Coulomb Counting is used as a basic current-integration baseline. Kalman-filter-based estimation is used as a conventional model-based recursive baseline. Factor graph optimization is evaluated as the main optimization-based estimation method.

### 3.1 Coulomb Counting

Coulomb Counting estimates SOC by integrating the measured battery current over time. In discrete time, the SOC update equation can be written as:

\[
SOC_k = SOC_{k-1} - \frac{\eta I_k \Delta t_k}{Q}
\]

where \(SOC_k\) is the estimated SOC at sample \(k\), \(\eta\) is the coulombic efficiency, \(I_k\) is the measured current, \(\Delta t_k\) is the sampling interval, and \(Q\) is the available battery capacity.

Coulomb Counting is simple and computationally efficient. However, it is sensitive to the initial SOC value, current sensor error, and capacity uncertainty. Under battery aging conditions, the available capacity decreases gradually. If the capacity value is not updated properly, the SOC estimation error may accumulate over time. Therefore, Coulomb Counting is used in this paper as a basic reference method for evaluating the benefit of model-based and optimization-based methods.

In this study, the initial SOC at the beginning of each discharge cycle is set to 1.0. The measured discharge capacity of each cycle is used as the capacity value for reconstructing the reference SOC. For baseline estimation, both cycle-specific capacity and nominal-capacity settings can be considered to analyze the influence of capacity uncertainty.

### 3.2 Kalman-Filter-Based Estimation

Kalman-filter-based methods estimate SOC recursively by combining a battery state transition model with voltage measurements. In a simplified SOC estimation problem, the state transition model can be derived from the current integration equation:

\[
SOC_k = SOC_{k-1} - \frac{\eta I_k \Delta t_k}{Q} + w_k
\]

where \(w_k\) represents process noise. The voltage measurement equation can be expressed as:

\[
V_k = h(SOC_k, I_k, \theta) + v_k
\]

where \(V_k\) is the measured terminal voltage, \(h(\cdot)\) is the voltage prediction function, \(\theta\) represents battery model parameters, and \(v_k\) represents measurement noise.

For linear systems, the standard Kalman Filter can be applied. For nonlinear battery voltage models, the Extended Kalman Filter or Unscented Kalman Filter is usually required. In this paper, a Kalman-filter-based estimator is considered as a conventional model-based baseline. Its recursive structure makes it computationally efficient, but its performance depends on the accuracy of the battery model, the noise covariance settings, and the validity of linearization assumptions.

The purpose of including a Kalman-filter-based method is to compare recursive estimation with optimization-based estimation under the same public experimental battery data. This comparison helps clarify whether FGO provides practical advantages under real measurement noise and aging-induced capacity variation.

### 3.3 Factor Graph Optimization

Factor graph optimization formulates SOC estimation as an optimization problem over a sequence of battery states. In the factor graph representation, each SOC state is represented as a variable node, and each model or measurement constraint is represented as a factor node. The optimal SOC trajectory is obtained by minimizing the total residual error associated with all factors.

For SOC estimation, the dynamic factor is derived from the current integration relationship between consecutive SOC states:

\[
r_{d,k} = SOC_k - SOC_{k-1} + \frac{\eta I_k \Delta t_k}{Q}
\]

where \(r_{d,k}\) is the dynamic residual. The voltage measurement factor is defined as:

\[
r_{v,k} = V_k - h(SOC_k, I_k, \theta)
\]

where \(r_{v,k}\) is the voltage measurement residual. A prior factor is also added to constrain the initial SOC value at the beginning of each discharge cycle:

\[
r_p = SOC_0 - \hat{SOC}_0
\]

where \(\hat{SOC}_0\) is the assumed initial SOC.

The FGO objective function can be written as:

\[
\min_{\{SOC_k\}} \sum_k \|r_{d,k}\|^2_{\Sigma_d^{-1}} + \sum_k \|r_{v,k}\|^2_{\Sigma_v^{-1}} + \|r_p\|^2_{\Sigma_p^{-1}}
\]

where \(\Sigma_d\), \(\Sigma_v\), and \(\Sigma_p\) represent the covariance or weighting terms of the dynamic, voltage measurement, and prior factors, respectively.

Compared with Coulomb Counting, FGO can use both current-based dynamic constraints and voltage-based measurement constraints. Compared with recursive Kalman-filter-based estimation, FGO can optimize multiple states jointly and perform smoothing over a state sequence. This makes FGO potentially more robust under real experimental measurement noise and cycle-to-cycle variation.

### 3.4 Application to Public Battery Aging Data

When applying FGO to public battery aging data, several practical issues must be considered. First, the available capacity changes as the battery ages. Therefore, the capacity value used in the dynamic factor should be selected carefully. Second, the voltage-SOC relationship may vary across cycles because of aging, temperature variation, and internal resistance change. Third, the reference SOC is reconstructed from discharge capacity and is not directly measured.

In this study, FGO is evaluated on selected discharge cycles from different aging stages. The same preprocessing procedure and evaluation metrics are applied to all methods. This allows the estimation performance of FGO to be compared with baseline methods under consistent experimental conditions.


## 4. Experimental Design and Evaluation Metrics

### 4.1 Experimental Objective

The objective of the experiments is to evaluate the applicability of FGO-based SOC estimation under real battery aging conditions. Unlike controlled simulation experiments, the public battery aging dataset contains real measurement noise, capacity degradation, cycle-to-cycle variation, and changes in voltage response. These characteristics make it suitable for investigating whether FGO can maintain stable SOC estimation performance when applied to experimental battery data.

The experiments are designed to answer the following research questions:

1. Can FGO estimate SOC accurately using public experimental lithium-ion battery discharge data?
2. How does SOC estimation performance change from early aging stages to late aging stages?
3. Compared with conventional baseline methods, does FGO provide more stable estimation under real measurement conditions?
4. How is SOC estimation error related to capacity degradation across discharge cycles?

### 4.2 Selected Battery and Aging Stages

Battery B0005 is used as the first evaluation object in this study. From the original NASA MATLAB data file, 168 discharge cycles are extracted and converted into a unified CSV format. Each discharge cycle contains measured current, terminal voltage, temperature, time, measured discharge capacity, and reconstructed reference SOC.

To analyze the influence of battery aging, three representative discharge cycles are selected:

\[
\text{early stage: cycle 1}
\]

\[
\text{middle stage: cycle 84}
\]

\[
\text{late stage: cycle 168}
\]

These cycles represent the beginning, middle, and end of the extracted aging sequence. The early-stage cycle corresponds to a relatively fresh battery condition, while the late-stage cycle corresponds to a more degraded battery condition. The middle-stage cycle provides an intermediate aging condition.

In addition to these three representative cycles, all 168 discharge cycles are used to construct the capacity degradation curve. This curve is used to analyze the relationship between battery aging and SOC estimation performance.

### 4.3 Experimental Cases

The experimental cases are organized as follows:

**Case 1: Early-stage SOC estimation.**  
SOC estimation is performed on discharge cycle 1 of battery B0005. This case evaluates the performance of different methods under a relatively fresh battery condition.

**Case 2: Middle-stage SOC estimation.**  
SOC estimation is performed on discharge cycle 84. This case evaluates the performance of different methods under an intermediate aging condition.

**Case 3: Late-stage SOC estimation.**  
SOC estimation is performed on discharge cycle 168. This case evaluates the performance of different methods under a more degraded battery condition.

**Case 4: Capacity degradation analysis.**  
The measured discharge capacity of all 168 discharge cycles is extracted and plotted against cycle index. This case provides a direct representation of the aging process of battery B0005.

**Case 5: Capacity-error relationship analysis.**  
After SOC estimation is performed across multiple cycles, the relationship between measured discharge capacity and SOC estimation error will be analyzed. This case is used to investigate whether estimation performance deteriorates as battery capacity decreases.

### 4.4 Compared Methods

Three SOC estimation methods are considered in this study:

1. Coulomb Counting,
2. Kalman-filter-based estimation,
3. Factor graph optimization.

Coulomb Counting serves as the simplest baseline method. It relies only on current integration and capacity information. Kalman-filter-based estimation serves as a conventional recursive model-based method. Factor graph optimization is the main method evaluated in this study.

All methods use the same preprocessed discharge cycle data. The reconstructed reference SOC is used as the evaluation reference. The same time, current, voltage, and capacity information are used to ensure a fair comparison.

### 4.5 Evaluation Metrics

The SOC estimation performance is evaluated using several quantitative metrics. Let \(SOC_{\mathrm{est},k}\) denote the estimated SOC at sample \(k\), and let \(SOC_{\mathrm{ref},k}\) denote the reconstructed reference SOC. The estimation error is defined as:

\[
e_k = SOC_{\mathrm{est},k} - SOC_{\mathrm{ref},k}
\]

The root mean square error is calculated as:

\[
RMSE = \sqrt{\frac{1}{N}\sum_{k=1}^{N} e_k^2}
\]

where \(N\) is the number of samples in the selected discharge cycle.

The mean absolute error is calculated as:

\[
MAE = \frac{1}{N}\sum_{k=1}^{N} |e_k|
\]

The maximum absolute error is calculated as:

\[
MaxError = \max_k |e_k|
\]

The standard deviation of the estimation error is calculated as:

\[
STD = \sqrt{\frac{1}{N}\sum_{k=1}^{N}(e_k-\bar{e})^2}
\]

where \(\bar{e}\) is the mean estimation error.

RMSE and MAE are used to evaluate overall estimation accuracy. Maximum absolute error is used to evaluate worst-case deviation. Error standard deviation is used to evaluate the stability of the estimation error. Together, these metrics provide a comprehensive evaluation of SOC estimation performance under different aging conditions.

### 4.6 Figure and Table Design

The experimental results will be presented using both figures and tables. The planned figures include:

1. Voltage, current, and reconstructed SOC curves for representative discharge cycles.
2. Capacity degradation curve of battery B0005 across 168 discharge cycles.
3. SOC estimation comparison curves for early, middle, and late aging stages.
4. SOC estimation error curves for different methods.
5. RMSE variation across selected cycles or aging stages.
6. Relationship between measured capacity and SOC estimation error.

The planned tables include:

1. Summary of selected discharge cycles.
2. Quantitative SOC estimation errors for early-stage, middle-stage, and late-stage cycles.
3. Comparison of RMSE, MAE, maximum error, and error standard deviation for all methods.
4. Capacity and estimation error summary across aging stages.

This experimental design allows both visual and quantitative comparison of different SOC estimation methods under real battery aging conditions.


## 5. Results and Discussion

### 5.1 Dataset Characteristics and Capacity Degradation

The extracted B0005 dataset contains 168 discharge cycles. Each discharge cycle includes measured terminal voltage, current, temperature, time, and measured discharge capacity. Based on the extracted discharge profiles, reference SOC trajectories were reconstructed using the measured capacity of each cycle.

The capacity degradation curve shows a clear decrease in measured discharge capacity over repeated discharge cycles. The measured capacity of the first discharge cycle is 1.8565 Ah, which is used as the initial reference capacity in this study. For the representative aging-stage cycles, the measured capacities are 1.8565 Ah for cycle 1, 1.5489 Ah for cycle 84, and 1.3251 Ah for cycle 168. The corresponding capacity ratios relative to cycle 1 are 1.0000, 0.8343, and 0.7138, respectively.

These results confirm that the selected cycles represent different aging stages of battery B0005. Cycle 1 represents the early stage, cycle 84 represents the middle stage, and cycle 168 represents the late stage. The significant decrease in measured capacity indicates that battery aging should not be ignored in SOC estimation. Since the available capacity appears directly in current-integration-based SOC estimation models, capacity degradation can introduce substantial estimation error if the capacity value is not updated.

The representative voltage, current, and reconstructed SOC curves also show that the discharge duration and voltage response vary across aging stages. These variations reflect real experimental characteristics that are not fully captured by simplified simulation models. Therefore, the public battery aging dataset provides a meaningful basis for evaluating SOC estimation methods under realistic aging conditions.

### 5.2 Coulomb Counting Baseline and Capacity Degradation Effect

Two Coulomb Counting settings were evaluated. The first setting uses the measured capacity of each discharge cycle. The second setting fixes the capacity to the measured capacity of cycle 1 and uses it as the nominal capacity for all selected aging-stage cycles.

When the measured capacity of each individual discharge cycle is used, the Coulomb Counting result is almost identical to the reconstructed reference SOC. The RMSE values for cycle 1, cycle 84, and cycle 168 are on the order of \(10^{-17}\). This result is expected because both the reconstructed reference SOC and the cycle-specific Coulomb Counting estimator are based on the same current integration and the same measured cycle capacity. Therefore, this result should not be interpreted as a practical advantage of Coulomb Counting. Instead, it verifies the consistency of the data preprocessing, reference SOC reconstruction, and metric calculation procedures.

In contrast, when the capacity of cycle 1 is fixed as the nominal capacity, the SOC estimation error increases significantly as the battery ages. For cycle 1, the RMSE remains nearly zero because the nominal capacity is equal to the measured capacity of that cycle. For cycle 84, where the capacity ratio decreases to approximately 0.8343, the RMSE increases to approximately 0.1041. For cycle 168, where the capacity ratio further decreases to approximately 0.7138, the RMSE increases to approximately 0.1881.

This result demonstrates that capacity degradation has a direct impact on current-integration-based SOC estimation. If a battery management system continues to use the initial nominal capacity while the actual available capacity decreases, SOC estimation error will accumulate and become increasingly significant in later aging stages. Therefore, aging-aware capacity information or additional measurement constraints are necessary for reliable SOC estimation over the battery lifetime.

The nominal-capacity Coulomb Counting result also provides a useful motivation for evaluating model-based and optimization-based methods. Since factor graph optimization can incorporate both dynamic constraints and voltage measurement constraints, it may provide a more flexible framework for SOC estimation under aging conditions. The following sections will further evaluate whether FGO can improve SOC estimation stability compared with conventional baseline methods.


### 5.3 FGO-Based SOC Estimation Results

After evaluating the Coulomb Counting baselines, FGO-based SOC estimation was further investigated using the selected aging stages of battery B0005. Three representative discharge cycles were used: cycle 1 for the early stage, cycle 84 for the middle aging stage, and cycle 168 for the late aging stage. The objective was to examine whether the FGO framework could reduce the SOC estimation error caused by capacity degradation.

A fixed-capacity FGO was first implemented. In this case, the capacity was fixed to the initial capacity of cycle 1, while a voltage factor was added using an empirical voltage-SOC relationship fitted from the early-stage discharge data. This method provided only limited improvement over nominal-capacity Coulomb Counting. For cycle 84, the RMSE decreased from 0.1041 to 0.0889. For cycle 168, the RMSE decreased only slightly from 0.1881 to 0.1837. These results indicate that simply adding a voltage factor is insufficient when the capacity is still assumed to be constant. The effectiveness of FGO under aging conditions depends strongly on whether the model can account for capacity degradation.

To address this limitation, a physically constrained capacity-aware FGO formulation was introduced. Instead of treating all SOC states as independent optimization variables, the SOC trajectory was parameterized using the cumulative discharged capacity and an estimated effective capacity. The SOC at time step \(k\) was expressed as

\[
SOC_k = 1 - \frac{Q_{\mathrm{dis}}(k)}{Q_{\mathrm{eff}}},
\]

where \(Q_{\mathrm{dis}}(k)\) is the cumulative discharged capacity and \(Q_{\mathrm{eff}}\) is the effective capacity estimated by the optimization. This formulation guarantees a physically consistent monotonic SOC decrease during discharge and avoids non-physical SOC recovery in the late-discharge region.

The physically constrained capacity-aware FGO significantly improved the SOC estimation accuracy. In cycle 84, the RMSE was reduced from 0.1041 for nominal-capacity Coulomb Counting to 0.0089. In cycle 168, the RMSE was reduced from 0.1881 to 0.0196. These results correspond to RMSE reductions of approximately 91.5% and 89.5%, respectively. The estimated effective capacities were also close to the reconstructed cycle capacities. For cycle 84, the true cycle capacity was 1.5489 Ah and the estimated capacity was 1.5717 Ah. For cycle 168, the true cycle capacity was 1.3251 Ah and the estimated capacity was 1.3669 Ah.

Figure X compares the SOC trajectories for the late-stage cycle 168. The nominal-capacity Coulomb Counting method overestimates SOC because it uses the initial capacity and does not account for aging-induced capacity loss. In contrast, the physically constrained capacity-aware FGO produces a monotonic SOC trajectory that closely follows the reconstructed reference SOC. A small residual offset remains near the end of discharge, mainly because the estimated effective capacity is slightly higher than the reconstructed cycle capacity.

Figure Y summarizes the RMSE comparison among nominal-capacity Coulomb Counting, fixed-capacity FGO, and physically constrained capacity-aware FGO. The results show that the main advantage of FGO in aged battery SOC estimation is not merely the inclusion of a voltage factor, but the ability to incorporate capacity-related parameters into a unified optimization framework.


### 5.4 Quantitative Comparison of SOC Estimation Methods

Table X summarizes the SOC estimation performance of the three methods for B0005 under different aging stages. The nominal-capacity Coulomb Counting method shows increasing error as the battery ages because it uses the initial capacity throughout all cycles. The fixed-capacity FGO provides only limited improvement, indicating that the voltage factor alone is insufficient when the capacity remains fixed. In contrast, the physically constrained capacity-aware FGO significantly reduces the SOC estimation error in both the middle and late aging stages by estimating the effective capacity and enforcing a monotonic discharge trajectory.

Table X. SOC estimation performance comparison for B0005 under different aging stages.

| Stage | Cycle | Method | True Capacity (Ah) | Estimated Capacity (Ah) | RMSE | MAE | Max Error |
|---|---:|---|---:|---:|---:|---:|---:|
| early | 1 | Nominal-Capacity CC | 1.8565 | - | 0.0000 | 0.0000 | 0.0000 |
| early | 1 | Fixed-Capacity FGO | 1.8565 | - | 0.0169 | 0.0120 | 0.0671 |
| early | 1 | Physical CA-FGO | 1.8565 | 1.8288 | 0.0081 | 0.0066 | 0.0149 |
| middle | 84 | Nominal-Capacity CC | 1.5489 | - | 0.1041 | 0.0904 | 0.1654 |
| middle | 84 | Fixed-Capacity FGO | 1.5489 | - | 0.0889 | 0.0605 | 0.3685 |
| middle | 84 | Physical CA-FGO | 1.5489 | 1.5717 | 0.0089 | 0.0078 | 0.0145 |
| late | 168 | Nominal-Capacity CC | 1.3251 | - | 0.1881 | 0.1640 | 0.2857 |
| late | 168 | Fixed-Capacity FGO | 1.3251 | - | 0.1837 | 0.1395 | 0.5453 |
| late | 168 | Physical CA-FGO | 1.3251 | 1.3669 | 0.0196 | 0.0172 | 0.0305 |