import time
from itertools import combinations

# 1. 基础配置
file_name = 'T10I4D100K.dat'
min_support = 500  # 支持度阈值 s
min_confidence = 0.6  # 置信度阈值 c (例如 60%)

print(f"=== 开始执行 A-Priori 算法与关联规则挖掘 ===")
start_total_time = time.time()

# --- 第一步：统计单品 (L1) ---
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

print(f"[L1] 频繁单品数量: {len(L1)} (耗时: {time.time() - start_time:.4f} 秒)")

# --- 第二步：循环生成 L2, L3, L4... (频繁项集) ---
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
                    is_candidate_valid = True
                    for sub_comb in combinations(comb, k - 1):
                        if frozenset(sub_comb) not in current_frequent:
                            is_candidate_valid = False
                            break

                    if is_candidate_valid:
                        candidate_counts[comb_set] = candidate_counts.get(comb_set, 0) + 1

    Lk = {itemset: count for itemset, count in candidate_counts.items() if count >= min_support}

    if not Lk:
        print(f"[L{k}] 没有找到满足条件的频繁 {k} 元组合，频繁项集搜索结束。")
        break

    frequent_items[k] = Lk
    print(f"[L{k}] 频繁 {k} 元组合数量: {len(Lk)} (耗时: {time.time() - start_time:.4f} 秒)")

    k += 1

# --- 第三步：生成关联规则 (Association Rules) 附加题部分 ---
print(f"\n--- 开始生成关联规则 (Min Confidence = {min_confidence}) ---")
association_rules = []

# 我们从长度 >= 2 的频繁项集中提取规则
for level in range(2, len(frequent_items) + 1):
    if level not in frequent_items:
        continue

    for itemset, support_xy in frequent_items[level].items():
        # 对于每一个频繁项集，尝试所有可能的拆分 X -> (itemset - X)
        for i in range(1, len(itemset)):
            for antecedent in combinations(itemset, i):
                antecedent_set = frozenset(antecedent)
                consequent_set = itemset - antecedent_set

                # 查找 antecedent (X) 的支持度
                # X 的长度是 i，所以它在 frequent_items[i] 里面
                antecedent_support = frequent_items[i].get(antecedent_set)

                if antecedent_support:
                    confidence = support_xy / antecedent_support
                    if confidence >= min_confidence:
                        association_rules.append({
                            'rule': f"{set(antecedent_set)} -> {set(consequent_set)}",
                            'support': support_xy,
                            'confidence': confidence
                        })

print(f"成功生成满足条件的关联规则共: {len(association_rules)} 条")
if association_rules:
    print("前 5 条关联规则示例：")
    for idx, rule in enumerate(association_rules[:5], 1):
        print(f"  {idx}. 规则: {rule['rule']} | 支持度: {rule['support']} | 置信度: {rule['confidence']:.4f}")

end_total_time = time.time()
print(f"\n=== 全部任务执行完毕！总耗时: {end_total_time - start_total_time:.4f} 秒 ===")