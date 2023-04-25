# %%
import pandas as pd
import numpy as np
from collections import deque
# if __name__=='__main__':
#     calculate()



df=pd.read_excel('./sample_data.xlsx')
df.head(10)

def _dps(child):
    '''
    与えられた子要素から再帰的に親要素を呼び出しキューに追加する。
    '''
    global Q
    global depth_dict
    global child_par_dict
    # print(f'{child} given for dps')
    Q.append(child)
    # print("Q:::", Q)
    # 評価済ならスキップ
    if depth_dict[child]!=False:
        pass
    # 親要素を持たない(目的変数)ならスキップ
    elif child not in [a for a, b in child_par_dict.items()]:
        pass
    else:
        parent=child_par_dict[child][0]
        _dps(parent)        

    return

# 親子関係を整理。 keyは子の変数、valueは [親の変数, 係数]。
child_par_dict={}
len_table=df.shape[0]
for i in range(0, len_table):
    child_par_dict[df.loc[i, 'children'] ] = [ df.loc[i, 'parent'], df.loc[i, 'coefficient']]


print('child_par_dict:')
print(child_par_dict)

# 深さをdictに記録する。未踏の場合はFalse
list_items = list(set([k for k, _ in child_par_dict.items() ] + [v[0] for _ , v in child_par_dict.items() ]))
depth_dict={}
for x in list_items:
    depth_dict[x]=False


# 深さ優先探索を行い、各変数の深さの情報を記録する
for k, _ in child_par_dict.items():
    Q=deque()
    _dps(k)

    # print('DEPTH_DICT:', depth_dict)
    Q=list(Q)[::-1] # 子->親->...の順を親->子->...の順に並び替える
    # print(f'Q: {Q}')
    if depth_dict[Q[0]]==False:
        base_depth=0
    else:
        base_depth=depth_dict[Q[0]]

    for i in range(0, len(Q)):
        depth_dict[Q[i]]=base_depth+i
    # print(f'depth_dict: {depth_dict}')


# 各変数(子変数)に対し、[子変数名、親変数名、深さ、係数、同じ深さの係数間での比率、深さ0の変数に対する比率 ]を計算し、出力
columns=['child_col', 'parent_col', 'depth', 'coef', 'coef_composition_ratio', 'root_ratio']
res_df=pd.DataFrame(columns=columns)
for i in range(0, max([v for _, v in depth_dict.items()])+1):
    # print(i, '*'*40)
    compare_cols = [k for k, v in depth_dict.items() if v == i]
    # print(compare_cols)

    for child_col in compare_cols:
        _depth=depth_dict[child_col]

        if i==0:
            _coef=1
            _coef_sum=1
            _parent_col='n/a'
            #_coef_composition_ratio=1
            #_root_ratio=1
        else:
            _coef=child_par_dict[child_col][1]
            _coef_sum=sum([child_par_dict[k][1] for k in compare_cols])
            _parent_col=child_par_dict[child_col][0]
            # _coef_composition_ratio=_coef / _coef_sum
            # _root_ratio= _coef_composition_ratio * res_df.loc[res_df['child_col']==_parent_col, 'root_ratio'].item()
        
        _df=pd.DataFrame([
            [child_col,_parent_col, _depth, _coef, np.NaN, np.NaN]],
            columns=columns
        )
        res_df=pd.concat([res_df, _df],axis=0).reset_index(drop=True)


res_df['coef_composition_ratio']=res_df.groupby(['parent_col'])['coef'].apply(lambda e: e/e.sum())
res_df['root_ratio'] = res_df.apply(lambda x: x['coef_composition_ratio'] * \
                                    res_df.loc[ res_df['child_col']==x['parent_col'], 'root_ratio'].item()
                                    if x['parent_col'] in np.unique(res_df['child_col']) else 1, axis=1
                        )
# res_df.apply(
#                             lambda x: x['coef_composition_ratio'] * res_df.loc[ res_df['child_col']==x['parent_col'], 'root_ratio'].item()
#                             if x['parent_col'] in np.unique(res_df['child_col']) else 1,
#                             axis=1
#                         )

print('RESULT:')
print(res_df)

# print(res_df.head)

#print(res_df.loc[res_df['child_col']==_parent_col, 'root_ratio'].item())

res_df.to_csv('./res.csv',encoding='SJIS')

# %%
res_df.apply(
    lambda x: x['coef_composition_ratio'] * res_df.loc[ res_df['child_col']==x['parent_col'], 'root_ratio'].item()
    if x['parent_col'] in np.unique(res_df['child_col']) else 1, axis=1
)
#res_df