import matplotlib.pyplot as plt
import numpy as np

# Datos
years = [1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100]
populations = ["0.35–0.40", "0.43–0.50", "0.50–0.58", "0.60–0.68", "0.89–0.98", "1.56–1.71", "6.06–6.15", "c. 10–13"]

# Función para limpiar y convertir rangos de población
def clean_population_range(pop_range):
    if 'c. ' in pop_range:
        pop_range = pop_range.replace('c. ', '')
    low, high = pop_range.split('–')
    low = float(low)
    high = float(high) if high.replace('.', '', 1).isdigit() else float(high.split()[0])
    return low, high

# Preparar datos para la visualización
population_low = []
population_high = []

for pop in populations:
    low, high = clean_population_range(pop)
    population_low.append(low)
    population_high.append(high)

# Ajustar diferencia para las barras
population_diff = np.array(population_high) - np.array(population_low)

# Configurar la figura
fig, ax = plt.subplots(figsize=(14, 8))

# Ajustar el ancho de las barras
bar_width = 0.4

# Barras para el valor bajo
bar1 = ax.bar(np.array(years) - bar_width/2, population_low, width=bar_width, color='blue', label='Lower Estimate')

# Barras para la diferencia hacia el valor alto
bar2 = ax.bar(np.array(years) + bar_width/2, population_diff, bottom=population_low, width=bar_width, color='green', label='Upper Estimate')

# Ajustar las marcas del eje x para que estén centradas entre las barras
ax.set_xticks(years)

ax.set_title('World Population Estimates by Century')
ax.set_ylabel('Population (in billions)')
ax.set_xlabel('Year')

# Añadir leyenda
plt.legend()

# Tabla de valores
cell_text = []
for low, high in zip(population_low, population_high):
    cell_text.append([f"{low:.2f}", f"{high:.2f}"])
table = plt.table(cellText=cell_text, colLabels=['Lower Estimate', 'Upper Estimate'], rowLabels=years, loc='bottom', cellLoc='center', bbox=[0, -0.5, 1, 0.3])

# Ajustar layout para no cortar la tabla
plt.subplots_adjust(left=0.1, bottom=0.3)

plt.show()
