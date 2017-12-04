<template>
    <div :class="['content-wrap', wrapClass]">
        <div :class="['right-content']">
            <slot></slot>
        </div>
    </div>
</template>
<script>
    import { Picker } from 'vpui';
    export default{
        data(){
            return {
                wrapClass: ''
            }
        },
        components: {
            picker: Picker
        },
        methods: {
            miniAside(asideMini){
                if(asideMini){
                    this.wrapClass = 'content-wrap-large';
                }else{
                    this.wrapClass = '';
                }
            }
        }
    }
</script>
<style scoped>
    .content-wrap{
        flex: 1;
        position: relative;
        margin-left: 230px;
        min-height: 100%;
        background-color: #ecf0f5;
    }
    .content-wrap-large{
        margin-left: 50px;
    }
    .right-content{
        width: 100%;
        padding: 15px;
        padding-top: 65px;
    }
</style>