<template>
    <div class="line-textarea-wrap">
        <textarea class="text-line" :rows="rows">{{lineContent}}</textarea>
        <slot ref="textContentArea"></slot>
    </div>
</template>
<script>
    export default{
        data(){
            return{
                lineContent: '',
                textContent: ''
            }
        },
        props: {
            rows: {
                type: Number,
                default: 5
            }
        },
        methods: {
            setLine(text){
                if (!text) {
                    this.lineContent = 1;
                    return;
                } 
                var line = 1;
                var str = '1';
                text.forEach((item, index, arr) => {
                    str += '\n' + ++line;
                });
                this.lineContent = str;
            }
        }
    }
</script>
<style scoped>
    .line-textarea-wrap{
        position: relative;
    }
    .text-line{
        background: #4b4040;
        color: #fff;
        height: 200px;
        overflow: hidden;
        width: 30px;
        border-right: 0;
        line-height: 20px;
        margin: 0px;
        padding: 0px;
        padding-left: 2px;
        text-align: center;
        border: 0;
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;

    }
    .domain-setting-area{
        background: #000;
        color: #fff;
        height: 200px;
        overflow: hidden;
        border-right: 0;
        line-height: 20px;
        margin: 0px;
        padding: 0px;
        padding-left: 2px;
        text-align: left;
        position: absolute;
        left: 28px;
        border: 0;
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
    }
</style>
<style>

</style>