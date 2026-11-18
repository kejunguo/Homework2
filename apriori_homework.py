import time
from itertools import combinations

# 1. Configuration & Parameters
file_name = 'T10I4D100K.dat'
min_support = 500  # Minimum support threshold (s)
min_confidence = 0.6  # Minimum confidence threshold (c) for association rules

print(f"=== Starting A-Priori Algorithm & Association Rule Mining ===")
print(f"Parameters: Min Support = {min_support}, Min Confidence = {min_confidence}")
start_total_time = time.time()

# --- Step 1: Count individual items (L1) ---
start_time = time.time()
item_counts = {}
transaction_count = 0

with open(file_name, 'r', encoding='utf-8') as file:
    for line in file:
        transaction_count += 1
        items = [int(item) for item in line.strip().split()]
        for item in items:
            item_counts[item] = item_counts.get(item, 0) + 1

frequent_items = {}
L1 = {frozenset([item]): count for item, count in item_counts.items() if count >= min_support}
frequent_items[1] = L1

print(f"[L1] Frequent 1-itemsets count: {len(L1)} (Elapsed time: {time.time() - start_time:.4f} s)")

# --- Step 2: Iteratively generate L2, L3, L4... (Frequent Itemsets) ---
k = 2
while True:
    start_time = time.time()
    current_frequent = frequent_items[k - 1]

    if not current_frequent:
        break

    prev_items = list(current_frequent.keys())
    candidate_counts = {}

    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            transaction_items = set(int(item) for item in line.strip().split())
            row_frequent_items = [item for item in transaction_items if frozenset([item]) in frequent_items[1]]

            if len(row_frequent_items) >= k:
                for comb in combinations(sorted(row_frequent_items), k):
                    comb_set = frozenset(comb)
                    # Apriori Pruning: Check if all subsets of size k-1 are frequent
                    is_candidate_valid = True
                    for sub_comb in combinations(comb, k - 1):
                        if frozenset(sub_comb) not in current_frequent:
                            is_candidate_valid = False
                            break

                    if is_candidate_valid:
                        candidate_counts[comb_set] = candidate_counts.get(comb_set, 0) + 1

    Lk = {itemset: count for itemset, count in candidate_counts.items() if count >= min_support}

    if not Lk:
        print(f"[L{k}] No frequent {k}-itemsets found. Halting itemset generation.")
        break

    frequent_items[k] = Lk
    print(f"[L{k}] Frequent {k}-itemsets count: {len(Lk)} (Elapsed time: {time.time() - start_time:.4f} s)")

    k += 1

# --- Step 3: Generate Association Rules (Optional Task / Bonus) ---
print(f"\n--- Generating Association Rules (Min Confidence = {min_confidence}) ---")
association_rules = []

# Extract rules from frequent itemsets of size >= 2
for level in range(2, len(frequent_items) + 1):
    if level not in frequent_items:
        continue

    for itemset, support_xy in frequent_items[level].items():
        # Try all possible splits: antecedent -> (itemset - antecedent)
        for i in range(1, len(itemset)):
            for antecedent in combinations(itemset, i):
                antecedent_set = frozenset(antecedent)
                consequent_set = itemset - antecedent_set

                # Retrieve support of the antecedent (X)
                antecedent_support = frequent_items[i].get(antecedent_set)

                if antecedent_support:
                    confidence = support_xy / antecedent_support
                    if confidence >= min_confidence:
                        association_rules.append({
                            'rule': f"{set(antecedent_set)} -> {set(consequent_set)}",
                            'support': support_xy,
                            'confidence': confidence
                        })

print(f"Total valid association rules generated: {len(association_rules)}")
if association_rules:
    print("Top 5 association rules example:")
    for idx, rule in enumerate(association_rules[:5], 1):
        print(f"  {idx}. Rule: {rule['rule']} | Support: {rule['support']} | Confidence: {rule['confidence']:.4f}")

end_total_time = time.time()
print(f"\n=== All tasks completed successfully! Total execution time: {end_total_time - start_total_time:.4f} s ===")