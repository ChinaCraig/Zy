"""
视觉模型相关路由
"""
from flask import Blueprint, request, jsonify

vision_bp = Blueprint('vision', __name__, url_prefix='/vision')


@vision_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    图像分析接口
    """
    pass


@vision_bp.route('/detect', methods=['POST'])
def detect():
    """
    目标检测接口
    """
    pass


@vision_bp.route('/recognize', methods=['POST'])
def recognize():
    """
    图像识别接口
    """
    pass


@vision_bp.route('/generate', methods=['POST'])
def generate():
    """
    图像生成接口
    """
    pass 