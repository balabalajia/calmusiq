class RhythmPatterns:
    """预定义的节奏型模板
    
    节奏型格式说明:
    - beat: 拍的位置，以四分音符为单位 (1.0=第一拍, 1.5=第一拍后的8分音符, 2.0=第二拍等)
    - drums: 该拍位置上同时演奏的鼓的列表
    - accent: 是否为重音
    
    示例:
    - beat=1.0: 第一拍 (四分音符位置)
    - beat=1.5: 第一拍和第二拍之间的8分音符位置
    - beat=2.0: 第二拍 (四分音符位置)
    """
    
    @staticmethod
    def standard_rock():
        """标准摇滚节奏型 - 底鼓1、3拍，军鼓2、4拍"""
        return [
            {'beat': 1.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 1.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 2.0, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 2.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 3.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 4.0, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 4.5, 'drums': ['closed_hihat'], 'accent': False},
        ]
    
    @staticmethod
    def disco_pattern():
        """迪斯科节奏型 - 四四拍每拍都有底鼓"""
        return [
            {'beat': 1.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 1.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 2.0, 'drums': ['bass', 'snare', 'closed_hihat'], 'accent': True},
            {'beat': 2.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 3.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 4.0, 'drums': ['bass', 'snare', 'closed_hihat'], 'accent': True},
            {'beat': 4.5, 'drums': ['closed_hihat'], 'accent': False},
        ]
    
    @staticmethod
    def shuffle_pattern():
        """Shuffle节奏型 - 三连音感觉"""
        return [
            {'beat': 1.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 1.67, 'drums': ['closed_hihat'], 'accent': False},  # 三连音的第二个音
            {'beat': 2.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 2.67, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.0, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 3.67, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 4.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 4.67, 'drums': ['closed_hihat'], 'accent': False},
        ]

    @staticmethod
    def funk_pattern():
        """放克节奏型 - 强调切分和休止"""
        return [
            {'beat': 1.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 1.25, 'drums': ['closed_hihat'], 'accent': False},  # 16分音符
            {'beat': 1.5, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 2.0, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 2.5, 'drums': ['bass'], 'accent': False},
            {'beat': 2.75, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.5, 'drums': ['bass', 'closed_hihat'], 'accent': False},
            {'beat': 4.0, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 4.5, 'drums': ['closed_hihat'], 'accent': False},
        ]
    
    @staticmethod
    def ballad_pattern():
        """抒情歌曲节奏型 - 简单稳定"""
        return [
            {'beat': 1.0, 'drums': ['bass', 'closed_hihat'], 'accent': True},
            {'beat': 2.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.0, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 4.0, 'drums': ['closed_hihat'], 'accent': False},
        ]
    
    @staticmethod
    def reggae_pattern():
        """雷鬼节奏型 - 强调后拍"""
        return [
            {'beat': 1.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 1.5, 'drums': ['bass', 'closed_hihat'], 'accent': False},
            {'beat': 2.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 2.5, 'drums': ['snare', 'closed_hihat'], 'accent': True},
            {'beat': 3.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 3.5, 'drums': ['bass', 'closed_hihat'], 'accent': False},
            {'beat': 4.0, 'drums': ['closed_hihat'], 'accent': False},
            {'beat': 4.5, 'drums': ['snare', 'closed_hihat'], 'accent': True},
        ]