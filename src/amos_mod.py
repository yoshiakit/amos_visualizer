# %%
import pandas as pd
import numpy as np
from collections import deque
from graphviz import Digraph

def _dps(child, Q, depth_dict, df):
        '''
        与えられた子要素から再帰的に親要素を呼び出しキューに追加する。
        '''
        
        # print(f'_dps called for {child}')
        Q.append(child)
        # 評価済ならスキップ
        if depth_dict[child]!=False:
            pass
        # 親要素を持たない変数(目的変数)ならスキップ
        elif child not in list(df['child']):
            # print(f'{child} not found as a child')
            pass
        else:
            parent=df.loc[df['child']==child, 'parent'].item()
            _dps(parent, Q, depth_dict, df)

        # print(f'Q is now {Q}')
        return

def calculate(path_data):
    df=pd.read_excel(path_data)
    list_items= list(set(list(df['parent']) + list(df['child'])))
    # print(f'list_items: \n{list_items}')

    # 深さ優先探索を行い、各変数の深さの情報を記録する
    depth_dict={}
    for x in list_items:
        depth_dict[x]=False

    for _, row in df.iterrows():
        Q=deque()
        _dps(row['child'], Q, depth_dict, df)
        
        Q=list(Q)[::-1] # 子->親->...の順を親->子->...の順に並び替える
        # print(f'Q: {Q}')

        if depth_dict[Q[0]]==False:
            base_depth=0
        else:
            base_depth=depth_dict[Q[0]]

        for i in range(0, len(Q)):
            depth_dict[Q[i]]=base_depth+i
    
    # print(f'depth_dict: {depth_dict}')
    
    # Note: 各変数(子変数)に対し、[子変数名, 親変数名,深さ, 係数]を計算し、格納
    columns=['child_col', 'parent_col', 'depth', 'coef'] 
    res_df=pd.DataFrame(columns=columns)
    for depth in range(0, max([t for _, t in depth_dict.items()])+1):
        compare_cols = [k for k, v in depth_dict.items() if v == depth]
        # print(f'depth: {depth}, columns: {compare_cols}')

        for child_col in compare_cols:
            # print(child_col)
            if depth==0:
                parent_col='n/a'
                coef=1
            else:
                parent_col=df.loc[df['child']==child_col, 'parent'].item()
                coef=df.loc[df['child']==child_col, '推定値'].item()
            
            _df=pd.DataFrame([[child_col, parent_col, depth, coef]], columns=columns)
            res_df=pd.concat([res_df, _df],axis=0).reset_index(drop=True)
    
    # 同じ親・深さの係数間での比率
    res_df['coef_composition_ratio'] = res_df.groupby(['parent_col'], group_keys=False)['coef'].\
        apply(lambda x: (x/x.sum())).astype('float64').round(5)
    
    # 深さ0の変数に対する比率
    def _get_root_ratio(row):
        parent_ratio=res_df.loc[res_df['child_col']==row['parent_col'],'coef_composition_ratio'].sum()
        return parent_ratio * row['coef_composition_ratio'] 

    res_df['root_ratio'] = res_df.apply(_get_root_ratio,axis=1).astype('float64').round(5).replace(0, 1)

    return res_df
    
def visualize(df, output_path='./tree'): 
    G = Digraph(format="png")
    G.attr("node", shape="box", fontname="MS Gothic")
    G.attr("edge", fontname="MS Gothic")

    for depth in np.unique(df['depth'].sort_values(ascending=True)):
        if depth == 0:
            continue

        _df = df.loc[df['depth']==depth, :]
        for _, row in _df.iterrows():
            G.edge( row['parent_col'], row['child_col'],
                label=f"係数：{np.round(row['coef'], 3)}\n" + \
                    f"構成比率: {np.round(100 * row['coef_composition_ratio'], 3)}%\n" + \
                    f"目的変数に対する寄与比率: {np.round(100 * row['root_ratio'], 3)}%",
                    dir='back'
                    )
    G.render(output_path)



if __name__=='__main__':
    df=calculate(path_data='../data/sample_data.xlsx')
    df.to_csv('../data/res_v2.csv',encoding='SJIS')
    visualize(df, output_path='./sample_result')

