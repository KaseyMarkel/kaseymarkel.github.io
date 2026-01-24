/**
 * BMS API Integration Module
 * Connects to BMS Pro API for real-time breeding data
 * Documentation: https://bmspro.io/1596/breeding-management-system/tutorials/
 */

class BMSAPIClient {
    constructor(config) {
        this.baseUrl = config.baseUrl || 'https://bmspro.io/api';
        this.apiKey = config.apiKey;
        this.programId = config.programId;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Generic API request handler with error handling and caching
     */
    async request(endpoint, options = {}) {
        const cacheKey = `${endpoint}-${JSON.stringify(options)}`;
        const cached = this.cache.get(cacheKey);

        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`BMS API Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            this.cache.set(cacheKey, { data, timestamp: Date.now() });
            return data;
        } catch (error) {
            console.error('BMS API Request Failed:', error);
            throw error;
        }
    }

    /**
     * Fetch trial data with filtering
     */
    async getTrialData(filters = {}) {
        const params = new URLSearchParams({
            programId: this.programId,
            ...filters
        });

        return await this.request(`/trials?${params}`);
    }

    /**
     * Fetch observations for specific traits
     */
    async getObservations(trialId, traits = []) {
        const params = new URLSearchParams({
            trialId,
            traits: traits.join(',')
        });

        return await this.request(`/observations?${params}`);
    }

    /**
     * Get germplasm data
     */
    async getGermplasm(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/germplasm?${params}`);
    }

    /**
     * Fetch funnel metrics (Block A)
     */
    async getFunnelMetrics(filters = {}) {
        try {
            const trials = await this.getTrialData(filters);

            // Aggregate data across trials
            const aggregated = {
                seedsPlanted: 0,
                plantsV4V6: 0,
                plantsSampled: 0,
                validGenotypes: 0,
                plantsSelected: 0,
                plantsPollinated: 0,
                successfulEars: 0,
                earsHarvested: 0
            };

            trials.forEach(trial => {
                if (trial.observations) {
                    aggregated.seedsPlanted += trial.observations.Seeds_Planted || 0;
                    aggregated.plantsV4V6 += trial.observations.Plants_V4V6 || 0;
                    aggregated.plantsSampled += trial.observations.Plants_Sampled || 0;
                    aggregated.validGenotypes += trial.observations.Valid_Genotypes || 0;
                    aggregated.plantsSelected += trial.observations.Plants_Selected || 0;
                    aggregated.plantsPollinated += trial.observations.Plants_Pollinated || 0;
                    aggregated.successfulEars += trial.observations.Successful_Ears || 0;
                    aggregated.earsHarvested += trial.observations.Ears_Harvested || 0;
                }
            });

            return [
                { name: 'Seeds Planted', value: aggregated.seedsPlanted },
                { name: 'Plants at V4-V6', value: aggregated.plantsV4V6 },
                { name: 'Plants Sampled', value: aggregated.plantsSampled },
                { name: 'Valid Genotypes', value: aggregated.validGenotypes },
                { name: 'Plants Selected', value: aggregated.plantsSelected },
                { name: 'Plants Pollinated', value: aggregated.plantsPollinated },
                { name: 'Successful Ears (>30k)', value: aggregated.successfulEars },
                { name: 'Ears Harvested', value: aggregated.earsHarvested }
            ];
        } catch (error) {
            console.error('Error fetching funnel metrics:', error);
            return [];
        }
    }

    /**
     * Calculate efficiency rates (Block B)
     */
    async getRateMetrics(filters = {}) {
        try {
            const funnel = await this.getFunnelMetrics(filters);

            const getValueByName = (name) => {
                const item = funnel.find(f => f.name === name);
                return item ? item.value : 0;
            };

            const seedsPlanted = getValueByName('Seeds Planted');
            const plantsV4V6 = getValueByName('Plants at V4-V6');
            const plantsSampled = getValueByName('Plants Sampled');
            const validGenotypes = getValueByName('Valid Genotypes');
            const plantsPollinated = getValueByName('Plants Pollinated');
            const successfulEars = getValueByName('Successful Ears (>30k)');
            const earsHarvested = getValueByName('Ears Harvested');

            const calculateRate = (numerator, denominator) => {
                return denominator > 0 ? (numerator / denominator) * 100 : 0;
            };

            const getStatus = (value, threshold, inverse = false) => {
                if (inverse) {
                    return value <= threshold ? 'green' : value <= threshold * 1.2 ? 'yellow' : 'red';
                }
                return value >= threshold ? 'green' : value >= threshold * 0.9 ? 'yellow' : 'red';
            };

            const emergenceRate = calculateRate(plantsV4V6, seedsPlanted);
            const samplingRate = calculateRate(plantsSampled, plantsV4V6);
            const validGenotypeRate = calculateRate(validGenotypes, plantsSampled);
            const pollinationSuccess = calculateRate(successfulEars, plantsPollinated);

            return [
                { name: 'Emergence Rate', value: emergenceRate, threshold: 80, status: getStatus(emergenceRate, 80) },
                { name: 'V4-V6 Survival', value: emergenceRate, threshold: 85, status: getStatus(emergenceRate, 85) },
                { name: 'Sampling Rate', value: samplingRate, threshold: 95, status: getStatus(samplingRate, 95) },
                { name: 'Valid Genotype Rate', value: validGenotypeRate, threshold: 90, status: getStatus(validGenotypeRate, 90) },
                { name: 'Pollination Success', value: pollinationSuccess, threshold: 85, status: getStatus(pollinationSuccess, 85) }
            ];
        } catch (error) {
            console.error('Error calculating rate metrics:', error);
            return [];
        }
    }

    /**
     * Fetch coverage metrics (Block C)
     */
    async getCoverageMetrics(filters = {}) {
        try {
            const trials = await this.getTrialData(filters);
            const coverageByScheme = new Map();

            trials.forEach(trial => {
                const scheme = `${trial.Scheme_ID} ${trial.Stage}`;
                const current = coverageByScheme.get(scheme) || { required: 0, available: 0 };

                current.required += trial.Plants_Required || 0;
                current.available += trial.Plants_Selected || 0;

                coverageByScheme.set(scheme, current);
            });

            return Array.from(coverageByScheme.entries()).map(([scheme, data]) => {
                const ratio = data.required > 0 ? data.available / data.required : 0;
                const status = ratio >= 1.2 ? 'green' : ratio >= 1.0 ? 'yellow' : 'red';

                return {
                    scheme,
                    required: data.required,
                    available: data.available,
                    ratio,
                    status
                };
            });
        } catch (error) {
            console.error('Error fetching coverage metrics:', error);
            return [];
        }
    }

    /**
     * Fetch cycle time metrics (Block D)
     */
    async getSpeedMetrics(filters = {}) {
        try {
            const trials = await this.getTrialData(filters);

            const calculateAverageDays = (field1, field2) => {
                let totalDays = 0;
                let count = 0;

                trials.forEach(trial => {
                    if (trial[field1] && trial[field2]) {
                        const date1 = new Date(trial[field1]);
                        const date2 = new Date(trial[field2]);
                        const days = Math.abs((date2 - date1) / (1000 * 60 * 60 * 24));
                        totalDays += days;
                        count++;
                    }
                });

                return count > 0 ? totalDays / count : 0;
            };

            const plantingToSampling = calculateAverageDays('Planting_Date', 'Sampling_Date');
            const samplingToGenotyping = calculateAverageDays('Sampling_Date', 'Genotyping_Result_Date');
            const genotypingToPlanting = calculateAverageDays('Genotyping_Result_Date', 'Next_Planting_Date');
            const totalCycle = calculateAverageDays('Planting_Date', 'Next_Planting_Date');

            return [
                { stage: 'Planting → Sampling', days: Math.round(plantingToSampling), target: 40 },
                { stage: 'Sampling → Genotyping', days: Math.round(samplingToGenotyping), target: 14 },
                { stage: 'Genotyping → Next Planting', days: Math.round(genotypingToPlanting), target: 21 },
                { stage: 'Total Cycle Time', days: Math.round(totalCycle), target: 75 }
            ].map(item => ({
                ...item,
                status: item.days <= item.target ? 'green' : 'yellow'
            }));
        } catch (error) {
            console.error('Error fetching speed metrics:', error);
            return [];
        }
    }

    /**
     * Identify top operational issues from trait data
     */
    async getTopIssues(filters = {}) {
        try {
            const trials = await this.getTrialData(filters);
            const issueTraits = {
                'Spiroplasma (Virus)': 'PLANTS_VIRUSsn',
                'Ear Mold Diseases': 'MAZ_PUDsn',
                'Out of Type Plants': 'Plantas_FueraDeTipo',
                'Pollination Failure': 'MALA_COBsn'
            };

            const issues = [];

            for (const [issue, trait] of Object.entries(issueTraits)) {
                let totalPlants = 0;
                let totalAffected = 0;

                trials.forEach(trial => {
                    if (trial.observations && trial.observations[trait] !== undefined) {
                        totalAffected += trial.observations[trait];
                        totalPlants += trial.observations.Plants_V4V6 || 0;
                    }
                });

                if (totalPlants > 0) {
                    issues.push({
                        issue,
                        plants: totalAffected,
                        pct: (totalAffected / totalPlants) * 100,
                        impact: totalAffected > 300 ? 'High' : totalAffected > 150 ? 'Medium' : 'Low'
                    });
                }
            }

            return issues.sort((a, b) => b.plants - a.plants).slice(0, 10);
        } catch (error) {
            console.error('Error fetching top issues:', error);
            return [];
        }
    }

    /**
     * Get trait pyramiding progress (Block F)
     */
    async getStackProgress(filters = {}) {
        try {
            const germplasm = await this.getGermplasm({ ...filters, scheme: 'Zn+QPM' });

            const levels = {
                '60': 0,
                '70': 0,
                '80': 0
            };

            germplasm.forEach(plant => {
                const znProgress = plant.Zn_progress || 0;
                const lysine = plant['Lys_%protein'] || 0;
                const tryptophan = plant['Trp_%protein'] || 0;
                const o2Status = plant.o2_status;

                if (znProgress >= 0.60 && lysine >= 0.30 && tryptophan >= 0.04) levels['60']++;
                if (znProgress >= 0.70 && lysine >= 0.35 && tryptophan >= 0.05) levels['70']++;
                if (znProgress >= 0.80 && lysine >= 0.40 && tryptophan >= 0.07 && o2Status === 'Homo') levels['80']++;
            });

            return [
                { level: 'Zn+QPM ≥60%', count: levels['60'], target: 200 },
                { level: 'Zn+QPM ≥70%', count: levels['70'], target: 120 },
                { level: 'Zn+QPM ≥80% + o2', count: levels['80'], target: 40 }
            ];
        } catch (error) {
            console.error('Error fetching stack progress:', error);
            return [];
        }
    }

    /**
     * Fetch all dashboard data at once
     */
    async getAllDashboardData(filters = {}) {
        try {
            const [
                funnelData,
                rateMetrics,
                coverageMetrics,
                speedMetrics,
                topIssues,
                stackProgress
            ] = await Promise.all([
                this.getFunnelMetrics(filters),
                this.getRateMetrics(filters),
                this.getCoverageMetrics(filters),
                this.getSpeedMetrics(filters),
                this.getTopIssues(filters),
                this.getStackProgress(filters)
            ]);

            return {
                funnelData,
                rateMetrics,
                coverageMetrics,
                speedMetrics,
                topIssues,
                stackProgress,
                lastUpdated: new Date().toISOString()
            };
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            throw error;
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BMSAPIClient;
}
