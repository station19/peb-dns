<template>
    <div class="box-header">
        <h3 class="box-title">{{domainName}}</h3>
        <btn @click="addRecord">添加</btn>
    </div>
    <div class="box-body">
        <grid :head="column" :data="gridData" style="margin-bottom: 10px;">
            <slot name>
            </slot>
            <div :slot="'cell:option_'+i" v-for="(item,i) in gridData" class="opt-column">
                <btn size="small" @click="edit(item)">编辑</btn>
                <btn @click="delete(item)" type="danger" size="small">删除</btn>
            </div>
        </grid>
        <vp-pager :total="pager.total" :current="pager.current" @to="pageTo" :position="'right'" :volumn="pager.volumn"></vp-pager>
    </div>
</template>
<script>
    import { grid,Pager } from 'vpui';
    export default{
        data(){
            return {
                column: [],
                gridData: [],
                pager:{
                    total: 0,
                    current: 1,
                    volumn: 10
                }
            }
        },
        components: {
            grid,
            vpPager: Pager
        },
        methods: {
            edit(item){
                console.log(item)
            },
            delete(item){
                console.log(item);
            },
            pageTo(index){

            }
        }
    }
</script>
<style>
    
</style>