<template>
    <div class="info-box">
        <i :class="'info-box-icon ion-ios-'+icon"></i>
        <div class="info-box-content">
            <span class="info-box-text"><slot></slot></span>
            <span class="info-box-number">{{count}}</span>
        </div>
    </div>
</template>
<script>
    export default{
        props: [
            /*icon: */
            'icon',
            'count'
        ]
    }
</script>
<style scroped>
    body .info-box{
        display: flex;
        min-height: 90px;
        background: #fff;
        width: 100%;
        box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        border-radius: 2px;
        margin-bottom: 15px;
        margin-right: 20px;
    }
    body .info-box-icon{
        width: 90px;
        height: 100%;
        display: block;
        text-align: center;
        line-height: 90px;
        font-size: 45px;
        color: #fff;
        background-color: #7CBDE8;
    }
    .info-box-content{
        flex: 1;
    }
.info-box-content span{color:#333;}
    .info-box-text, .info-box-number{
        display: block;
        font-size: 14px;
    }

    .info-box-number{
        font-size: 18px;
    }

</style>