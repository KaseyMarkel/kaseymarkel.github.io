// BMS API Integration Module
// Documentation: https://bmspro.io/1596/breeding-management-system/tutorials/maize-40/trial-data-collection

const BMSAPI = {
    config: {
        baseUrl: 'https://bmspro.io/api/v1',
        apiKey: '', // Set this in dashboard
        programId: '', // Set this in dashboard
        cache: new Map(),
        cacheTimeout: 5 * 60 * 1000 // 5 minutes
    },

    // Generic API request handler
    async request(endpoint, options = {}) {
        const url = `${this.config.baseUrl}${endpoint}`;
        const cacheKey = `${endpoint}-${JSON.stringify(options)}`;
        
        // Check cache
        const cached = this.config.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cacheTimeout) {
            console.log('📦 Using cached data for:', endpoint);
            return cached.data;
        }

        try {
            console.log('🌐 Fetching from BMS API:', endpoint);
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Authorization': `Bearer ${this.config.apiKey}`,
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`BMS API Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            // Cache the result
            this.config.cache.set(cacheKey, {
                data,
                timestamp: Date.now()
            });

            return data;
        } catch (error) {
            console.error('❌ BMS API request failed:', error);
            throw error;
        }
    },

    // Fetch all trials for the program
    async getTrials(filters = {}) {
        const params = new URLSearchParams({
            programId: this.config.programId,
            ...filters
        });
        return await this.request(`/trials?${params}`);
    },

    // Fetch observations for specific traits
    async getObservations(trialId, traits = []) {
        const params = new URLSearchParams({
            trialId,
            variables: traits.join(',')
        });
        return await this.request(`/observations?${params}`);
    },

    // Get germplasm data
    async getGermplasm(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/germplasm?${params}`);
    },

    // Aggregate funnel metrics from trials
    async getFunnelMetrics() {
        try {
            const trials = await this.getTrials();
            
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
                aggregated.seedsPlanted += trial.Seeds_Planted || 0;
                aggregated.plantsV4V6 += trial.Plants_V4V6 || 0;
                aggregated.plantsSampled += trial.Plants_Sampled || 0;
                aggregated.validGenotypes += trial.Valid_Genotypes || 0;
                aggregated.plantsSelected += trial.Plants_Selected || 0;
                aggregated.plantsPollinated += trial.Plants_Pollinated || 0;
                aggregated.successfulEars += trial.Successful_Ears || 0;
                aggregated.earsHarvested += trial.Ears_Harvested || 0;
            });

            return [
                { name: 'Seeds Planted', value: aggregated.seedsPlanted, target: aggregated.seedsPlanted },
                { name: 'Plants at V4-V6', value: aggregated.plantsV4V6, target: aggregated.plantsV4V6 },
                { name: 'Plants Sampled', value: aggregated.plantsSampled, target: aggregated.plantsSampled },
                { name: 'Valid Genotypes', value: aggregated.validGenotypes, target: aggregated.validGenotypes },
                { name: 'Plants Selected', value: aggregated.plantsSelected, target: aggregated.plantsSelected },
                { name: 'Plants Pollinated', value: aggregated.plantsPollinated, target: aggregated.plantsPollinated },
                { name: 'Successful Ears (>30k)', value: aggregated.successfulEars, target: aggregated.successfulEars },
                { name: 'Ears Harvested', value: aggregated.earsHarvested, target: aggregated.earsHarvested }
            ];
        } catch (error) {
            console.error('Error fetching funnel metrics:', error);
            return null;
        }
    },

    // Calculate rate metrics from trials
    async getRateMetrics() {
        try {
            const funnel = await this.getFunnelMetrics();
            if (!funnel) return null;

            const getValue = (name) => funnel.find(f => f.name === name)?.value || 0;

            const seedsPlanted = getValue('Seeds Planted');
            const plantsV4V6 = getValue('Plants at V4-V6');
            const plantsSampled = getValue('Plants Sampled');
            const validGenotypes = getValue('Valid Genotypes');
            const plantsPollinated = getValue('Plants Pollinated');
            const successfulEars = getValue('Successful Ears (>30k)');

            const calcRate = (num, den) => den > 0 ? (num / den) * 100 : 0;
            const getStatus = (val, thresh) => val >= thresh ? 'green' : val >= thresh * 0.9 ? 'yellow' : 'red';

            return [
                { name: 'Emergence Rate', value: calcRate(plantsV4V6, seedsPlanted), threshold: 80, status: getStatus(calcRate(plantsV4V6, seedsPlanted), 80) },
                { name: 'V4-V6 Survival', value: calcRate(plantsV4V6, seedsPlanted), threshold: 85, status: getStatus(calcRate(plantsV4V6, seedsPlanted), 85) },
                { name: 'Sampling Rate', value: calcRate(plantsSampled, plantsV4V6), threshold: 95, status: getStatus(calcRate(plantsSampled, plantsV4V6), 95) },
                { name: 'Valid Genotype Rate', value: calcRate(validGenotypes, plantsSampled), threshold: 90, status: getStatus(calcRate(validGenotypes, plantsSampled), 90) },
                { name: 'Pollination Success', value: calcRate(successfulEars, plantsPollinated), threshold: 85, status: getStatus(calcRate(successfulEars, plantsPollinated), 85) }
            ];
        } catch (error) {
            console.error('Error calculating rate metrics:', error);
            return null;
        }
    },

    // Initialize with API credentials
    init(apiKey, programId) {
        this.config.apiKey = apiKey;
        this.config.programId = programId;
        console.log('✅ BMS API initialized');
    },

    // Clear cache
    clearCache() {
        this.config.cache.clear();
        console.log('🗑️ Cache cleared');
    }
};

// Export for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BMSAPI;
}
