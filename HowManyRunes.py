import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 30  #value precyzyjnosci

# Constants
RUN_COST = 9750000 #koszt 1 runy AVG
MULTIPLIERS = [1, 10, 25, 100]
MULTIPLIER_BINDING = {1: 1, 10: 2, 25: 3, 100: 4}
BREAKPOINTS = [(25, 0), (50, 1), (100, 2), (250, 3), (500, 4),
               (1000, 5), (2500, 6), (5000, 7), (10000, 8), (float('inf'), 9)]


class Building:
    def __init__(self, id, name, initial_duration, initial_increment, initial_cost, initial_level):
        self.id = id
        self.name = name
        self.initial_duration = initial_duration
        self.initial_increment = initial_increment
        self.initial_cost = initial_cost
        self.initial_level = initial_level
        self.price_table = None
        self.breakpoint_cache = {}

    def get_upgrade_price(self, level, bulk):
        if bulk in MULTIPLIER_BINDING:
            amount = MULTIPLIER_BINDING[bulk]
            if level < len(self.price_table[amount - 1]):
                return self.price_table[amount - 1][level]
        return self.get_upgrade_price_unsafe(level, bulk)

    def get_upgrade_price_unsafe(self, level, bulk):
        return math.ceil(self.initial_cost * (1.03 ** level) * (1 - 1.03 ** bulk) / -0.03)

    def get_cycle_duration(self, level):
        return self.initial_duration * (0.8 ** self.get_nearest_breakpoint(level))

    def get_cycle_production(self, level):
        return round(self.initial_increment * level * (2 ** self.get_nearest_breakpoint(level)))

    def get_production_rate(self, level, run_multiplier=1):
        return (self.get_cycle_production(level) / self.get_cycle_duration(level)) * run_multiplier

    def get_nearest_breakpoint(self, level):
        if level not in self.breakpoint_cache:
            for threshold, bp in BREAKPOINTS:
                if level < threshold:
                    self.breakpoint_cache[level] = bp
                    break
        return self.breakpoint_cache[level]

    def generate_price_table(self, max_level):
        self.price_table = [[] for _ in range(len(MULTIPLIERS))]

        # Use Decimal for single-upgrade price table to avoid overflow
        self.price_table[0].append(Decimal(self.initial_cost))
        for j in range(1, max_level):
            self.price_table[0].append(math.ceil(self.price_table[0][j - 1] * Decimal('1.03')))

        #BULK
        for j in range(1, len(MULTIPLIERS)):
            bulk_size = MULTIPLIERS[j]
            for k in range(max_level - bulk_size):
                cost = sum(self.price_table[0][k + l] for l in range(bulk_size))
                self.price_table[j].append(cost)


buildings = [
    Building(0, "Seat", 72, 1, 5, 1),
    Building(1, "PopcornStand", 360, 10, 100, 0),
    Building(2, "ParkingLot", 720, 40, 2500, 0),
    Building(3, "Trap", 1080, 120, 50000, 0),
    Building(4, "Drinks", 1440, 320, 1000000, 0),
    Building(5, "DeadlyTrap", 2160, 960, 25000000, 0),
    Building(6, "VipSeat", 2880, 2560, 500000000, 0),
    Building(7, "Snacks", 4320, 7680, 10000000000, 0),
    Building(8, "StrayingMonsters", 8640, 30720, 250000000000, 0),
    Building(9, "Toilet", 21600, 153600, 5000000000000, 0)
]

for building in buildings:
    building.generate_price_table(25001)


def calculate_run_multiplier(collected_run):
    return max(1, int(collected_run // 20))


def get_valid_input(prompt, min_val, max_val=None):
    while True:
        try:
            value = float(input(prompt))
            if value < min_val or (max_val is not None and value >= max_val):
                print(f"Wartość musi być między {min_val} a {max_val - 1 if max_val else 'nieskończonością'}.")
            else:
                return value
        except ValueError:
            print("Proszę podać prawidłową liczbę.")


def get_yes_no_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ['t', 'tak', 'y', 'yes']:
            return True
        elif response in ['n', 'nie', 'no']:
            return False
        print("Proszę wpisać 'tak'/'t' lub 'nie'/'n'.")


def main_program():
    while True:
        try:
            print("Kalkulator produkcji run - by TomieR")
            print("---------------------------------------------")

           #Podanie wartosci budynku
            levels = [int(get_valid_input(f"Poziom {b.name}: ", 0)) for b in buildings]
            collected_run = get_valid_input("Zebrane runy (dla mnożnika): ", 0)

            #Podanie czasu
            days = int(get_valid_input("Podaj dni: ", 0))
            hours = int(get_valid_input("Podaj godziny: ", 0, 24))
            minutes = int(get_valid_input("Podaj minuty: ", 0, 60))

            #Detale
            show_details = get_yes_no_input("Czy chcesz wyświetlić szczegółowe informacje o produkcji budynków? (tak/nie): ")

            #Przeliczenie czasu
            total_seconds = (days * 86400) + (hours * 3600) + (minutes * 60)

            run_multiplier = calculate_run_multiplier(collected_run)
            bonus_percentage = run_multiplier * 100
            total_money = 0

            if show_details:
                print("\nSzczegółowa produkcja budynków:")
                for building, level in zip(buildings, levels):
                    base_production = building.get_production_rate(level, 1)
                    boosted_production = base_production * run_multiplier
                    total_money += boosted_production
                    print(f"{building.name}: {base_production:,.2f} $/s × {run_multiplier}x = {boosted_production:,.2f} $/s")
            else:
                #without info
                for building, level in zip(buildings, levels):
                    base_production = building.get_production_rate(level, 1)
                    total_money += base_production * run_multiplier

            run_production = total_money / RUN_COST
            runes_earned = run_production * total_seconds

            print("\nPodsumowanie:")
            print(f"Zebrane runy (mnożnik): {collected_run:,.0f}")
            print(f"Bonus do zarobków: +{bonus_percentage:,.0f}% (mnożnik: {run_multiplier}x)")
            print(f"Łączna produkcja: {total_money:,.2f} $/s")
            print(f"Produkcja run: {run_production:.6f} run/s")
            print(f"\nPo {days} dniach, {hours} godzinach i {minutes} minutach otrzymasz: {runes_earned:,.2f} run")

            # loop programu
            while True:
                restart = input("\nPowtórzyć kalkulacje? (T/N): ").strip().upper()
                if restart == 'N':
                    print("Kalkulator czasu run - by TomieR")
                    return
                elif restart == 'T':
                    break
                else:
                    print("Proszę wpisać 'T' lub 'N'")

        except KeyboardInterrupt:
            print("\nPrzerwano przez użytkownika.")
            return
        except Exception as e:
            print(f"\nWystąpił błąd: {str(e)}")
            print("Spróbuj ponownie.")


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        import os
        os.chdir(sys._MEIPASS)

    main_program()

    if getattr(sys, 'frozen', False):
        input("Naciśnij Enter, aby zakończyć...")