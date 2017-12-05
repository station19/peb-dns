<template>
<div class="box box-primary" v-if="exist">
    <div class="box-header with-border">
      <h3 class="box-title">{{ title }}</h3>
      <div class="box-tools pull-right">
        <button type="button" class="btn btn-box-tool" data-widget="collapse" @click="show = !show">
            <i class="fa fa-minus"></i>
        </button>
        <button type="button" class="btn btn-box-tool" data-widget="remove" @click="exist = !exist">
            <i class="fa fa-times"></i>
        </button>
      </div>
    </div>
    <transition name="box-body-slide">
        <div class="box-body" style="display: block;" v-show="show" ref="boxPanel">
            <div style="padding: 20px;">
                <slot></slot>
            </div>
        </div>
    </transition>
</div>
</template>
<script>
    export default{
        data(){
            return{
                show: true,
                exist: true,
            }
        },
        
        props: {
            title: String
        },
        
        methods:{
            toogleContent(){
                this.show = !this.show;
            }
        },

        mounted(){
            //console.log(window.coim)
            //console.log(this.$refs.boxPanel.offsetHeight);
            //this.$refs.boxPanel.style.height = '100px'
            //let boxPanel = this.$refs.boxPanel;
            //boxPanel.style.height = `${boxPanel.offsetHeight}px`;
        }
    }
</script>
<style scoped>
    .borad-title{
        height: 20px;
    }

    .box-body{
        overflow: hidden;
        padding: 0;
        width:100%;
    }

    .box-body-slide-enter-active, .box-body-slide-leave-active {
        transition: all .5s  ease
    }

    .box-body-slide-leave-to{
        height: 0px !important;
        opacity: 0;
    }

    .box-body-slide-enter  /* .fade-leave-active in below version 2.1.8 */ {
        height: 0px !important;
        opacity: 0;
    }
</style>