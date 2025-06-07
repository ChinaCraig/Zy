"""
语音模型相关路由
"""
from flask import Blueprint, request, jsonify

speech_bp = Blueprint('speech', __name__, url_prefix='/speech')


@speech_bp.route('/recognize', methods=['POST'])
def recognize():
    """
    语音识别接口
    """
    pass


@speech_bp.route('/synthesize', methods=['POST'])
def synthesize():
    """
    语音合成接口
    """
    pass


@speech_bp.route('/process', methods=['POST'])
def process():
    """
    语音处理接口
    """
    pass


@speech_bp.route('/convert', methods=['POST'])
def convert():
    """
    语音格式转换接口
    """
    pass 