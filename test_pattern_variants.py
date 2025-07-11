#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节奏型变体测试脚本
演示如何使用不同的预定义节奏型和变体功能
"""

from random_drumsheet import DrumSheetGenerator
from rhythm_patterns import RhythmPatterns
import random

def test_all_patterns():
    """测试所有预定义的节奏型"""
    print("测试所有预定义节奏型")
    print("=" * 50)
    
    # 获取所有节奏型方法
    pattern_methods = [
        ('standard_rock', RhythmPatterns.standard_rock),
        ('disco_pattern', RhythmPatterns.disco_pattern),
        ('shuffle_pattern', RhythmPatterns.shuffle_pattern),
        ('funk_pattern', RhythmPatterns.funk_pattern),
        ('ballad_pattern', RhythmPatterns.ballad_pattern),
        ('reggae_pattern', RhythmPatterns.reggae_pattern)
    ]
    
    for pattern_name, pattern_method in pattern_methods:
        print(f"\n处理节奏型: {pattern_name}")
        
        # 创建生成器
        generator = DrumSheetGenerator()
        
        # 获取原始节奏型
        original_pattern = pattern_method()
        
        # 生成原始版本
        generator.generate_from_pattern(original_pattern, bars=2)
        original_path = generator.save_midi(f"{pattern_name}_test.mid")
        
        # 生成随机变体
        variant_pattern = generator.create_pattern_variant(original_pattern, 'all')
        generator = DrumSheetGenerator()  # 重新初始化
        generator.generate_from_pattern(variant_pattern, bars=2)
        variant_path = generator.save_midi(f"{pattern_name}_variant_test.mid")

        print(f"  文件: {original_path}, {variant_path}")

def test_specific_variants():
    """测试特定的变体功能"""
    print("\n\n测试特定变体功能")
    print("=" * 50)
    
    # 选择一个节奏型进行详细测试
    pattern = RhythmPatterns.standard_rock()
    pattern_name = "standard_rock_detailed"
    
    generator = DrumSheetGenerator()
    
    # 测试不同的变体类型
    variant_types = ['snare', 'bass', 'random', 'all']
    
    for variant_type in variant_types:
        print(f"\n生成 {variant_type} 变体...")
        
        # 生成变体
        variant = generator.create_pattern_variant(pattern, variant_type)
        
        # 重新初始化生成器
        generator = DrumSheetGenerator()
        
        # 生成MIDI
        generator.generate_from_pattern(variant, bars=4)
        midi_path = generator.save_midi(f"{pattern_name}_{variant_type}.mid")

        print(f"  文件: {midi_path}")

def test_custom_probabilities():
    """测试自定义概率参数"""
    print("\n\n测试自定义概率参数")
    print("=" * 50)
    
    pattern = RhythmPatterns.standard_rock()
    generator = DrumSheetGenerator()
    
    # 测试不同的概率设置
    test_cases = [
        {'name': 'high_snare', 'snare_prob': 0.8, 'bass_prob': 0.1},
        {'name': 'high_bass', 'snare_prob': 0.1, 'bass_prob': 0.8},
        {'name': 'balanced', 'snare_prob': 0.3, 'bass_prob': 0.3},
    ]
    
    for case in test_cases:
        print(f"\n测试案例: {case['name']}")
        
        # 手动创建变体
        snare_variant = generator.add_random_snare(pattern, case['snare_prob'])
        final_variant = generator.add_random_bass(snare_variant, case['bass_prob'])
        
        # 生成MIDI
        generator = DrumSheetGenerator()
        generator.generate_from_pattern(final_variant, bars=4)
        midi_path = generator.save_midi(f"custom_prob_{case['name']}.mid")

        print(f"  文件: {midi_path}")

def main():
    """主测试函数"""
    print("节奏型变体功能测试")
    print("=" * 60)
    
    # 设置随机种子以获得可重复的结果
    random.seed(42)
    
    # 运行所有测试
    test_all_patterns()
    test_specific_variants()
    test_custom_probabilities()
    
    print("\n\n所有测试完成！")
    print("请检查 outputs/ 目录中生成的MIDI文件")

if __name__ == "__main__":
    main()