import pandas as pd
import matplotlib.pyplot as plt

# Data
years = [1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100]
populations = ["0.35–0.40", "0.43–0.50", "0.50–0.58", "0.60–0.68", "0.89–0.98", "1.56–1.71", "6.06–6.15", "c. 10–13"]
growth_rates = [">0%", "<0.12%", "0.15–0.3%", "0.1–0.15%", "0.3–0.5%", "0.5–0.6%", "1.3–1.4%", "0.7–0.8%"]

# Clean and convert data
def clean_population_range(pop_range):
    if 'c. ' in pop_range:
        pop_range = pop_range.replace('c. ', '')
    low, high = pop_range.split('–')
    low = float(low)
    high = float(high) if high.isnumeric() else float(high.split()[0])
    return low, high

population_low = []
population_high = []

for pop in populations:
    low, high = clean_population_range(pop)
    population_low.append(low)
    population_high.append(high)

# Create a dataframe
df = pd.DataFrame({
    'Year': years,
    'Population Low (billions)': population_low,
    'Population High (billions)': population_high,
    'Growth p.a.': growth_rates
})

# Plotting
fig, ax = plt.subplots(2, 1, figsize=(10, 10))

# Population plot
ax[0].fill_between(df['Year'], df['Population Low (billions)'], df['Population High (billions)'], color='skyblue', alpha=0.5)
ax[0].set_title('Estimated World Population by Year')
ax[0].set_ylabel('Population (in billions)')
ax[0].set_xlabel('Year')

# Growth rate plot
ax[1].bar(df['Year'], df['Growth p.a.'], color='green', alpha=0.7)
ax[1].set_title('Population Growth Rate per Annum')
ax[1].set_ylabel('Growth Rate')
ax[1].set_xlabel('Year')

plt.tight_layout()
plt.show()
