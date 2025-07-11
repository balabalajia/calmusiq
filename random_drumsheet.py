import yaml
import random
import os
import copy
from music21 import stream, note, meter, tempo, instrument, volume, converter
from rhythm_patterns import RhythmPatterns


class DrumSheetGenerator:
    """架子鼓乐谱生成器"""

    def __init__(self, midi_config_path="./configs/midi_config.yaml", run_config_path="./configs/run_configs.yaml"):
        """初始化生成器"""
        self.midi_config = self.load_yaml(midi_config_path)
        self.run_config = self.load_yaml(run_config_path)

        # 初始化音乐流
        self.score = stream.Stream()
        self.drum_part = stream.Part()

        # 设置基本参数
        self.bpm = self.run_config.get('bpm', 120)
        self.numerator = self.run_config.get('numerator', 4)
        self.denominator = self.run_config.get('denominator', 4)
        self.bars = self.run_config.get('bars', 4)

        # 设置拍号和速度
        self.score.insert(0, meter.TimeSignature(f'{self.numerator}/{self.denominator}'))
        self.score.insert(0, tempo.MetronomeMark(number=self.bpm))

        # 设置架子鼓乐器
        self.drum_part.insert(0, instrument.Percussion())

        # 获取概率参数
        self.base_note_length = self.run_config.get('base_note_length', 0.5)
        self.subdivision_prob = self.run_config.get('subdivision_probability', 0.1)
        self.triplet_prob = self.run_config.get('triplet_probability', 0.1)
        self.rest_prob = self.run_config.get('rest_probability', 0.3)
        self.double_note_prob = self.run_config.get('double_note_probability', 0.1)
        self.triple_note_prob = self.run_config.get('triple_note_probability', 0.1)
        self.accent_prob = self.run_config.get('accent_probability', 0.2)

        # 鼓的概率权重
        self.drum_probabilities = self.run_config.get('drum_probabilities', {})

    def load_yaml(self, file_path):
        """加载YAML配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"配置文件 {file_path} 未找到")
            return {}
        except yaml.YAMLError as e:
            print(f"YAML文件解析错误: {e}")
            return {}

    def add_note(self, note_names, note_duration, offset, is_accent=False):
        """向MIDI音轨添加音符

        Args:
            note_names: 音符名称，多个音符用|分隔
            note_duration: 音符持续时间（四分音符为单位）
            offset: 音符在小节中的偏移量
            is_accent: 是否为重音
        """
        if note_names == 'rest':
            # 添加休止符
            rest = note.Rest(quarterLength=note_duration)
            self.drum_part.insert(offset, rest)
            return

        # 处理多个同时发声的音符
        drums = note_names.split('|')

        for drum_name in drums:
            if drum_name in self.midi_config:
                midi_note = self.midi_config[drum_name]
                drum_note = note.Note(pitch=midi_note, quarterLength=note_duration)

                # 设置音量（重音/轻音）
                if is_accent:
                    drum_note.volume = volume.Volume(velocity=100)
                else:
                    drum_note.volume = volume.Volume(velocity=70)

                self.drum_part.insert(offset, drum_note)

    def generate_from_pattern(self, pattern, bars=1):
        """根据节奏型模板生成MIDI

        Args:
            pattern: 节奏型列表，每个元素包含beat, drums, accent
            bars: 重复小节数
        """
        self.drum_part = stream.Part()
        self.drum_part.insert(0, instrument.Percussion())

        # 检测是否包含三连音（beat值包含.67或.33）
        has_triplets = any(abs(note_info['beat'] % 1 - 0.67) < 0.01 or
                           abs(note_info['beat'] % 1 - 0.33) < 0.01
                           for note_info in pattern)

        if has_triplets:
            self._generate_triplet_pattern(pattern, bars)
        else:
            self._generate_regular_pattern(pattern, bars)

    def _generate_triplet_pattern(self, pattern, bars):
        """生成包含三连音的节奏型"""
        from music21 import duration

        for bar in range(bars):
            bar_offset = bar * self.numerator

            # 按拍分组处理
            beat_groups = {}
            for note_info in pattern:
                beat_int = int(note_info['beat'])
                if beat_int not in beat_groups:
                    beat_groups[beat_int] = []
                beat_groups[beat_int].append(note_info)

            for beat_num, notes_in_beat in beat_groups.items():
                beat_offset = bar_offset + beat_num - 1

                # 检查这一拍是否包含三连音
                triplet_notes = [n for n in notes_in_beat if abs(n['beat'] % 1 - 0.67) < 0.01]

                if triplet_notes:
                    # 处理三连音拍
                    self._add_triplet_beat(notes_in_beat, beat_offset)
                else:
                    # 处理普通拍
                    for note_info in notes_in_beat:
                        beat_fraction = note_info['beat'] % 1
                        note_offset = beat_offset + beat_fraction
                        drums_str = '|'.join(note_info['drums'])

                        # 计算音符时长
                        note_duration = self._calculate_note_duration_in_pattern(note_info, pattern)

                        self.add_note(drums_str, note_duration, note_offset, note_info['accent'])

    def _add_triplet_beat(self, notes_in_beat, beat_offset):
        """添加三连音拍"""
        from music21 import duration, note as music21_note

        # 创建三连音组
        triplet_duration = duration.Duration(quarterLength=2 / 3)  # 三连音中每个音符的时长

        # 按beat值排序
        sorted_notes = sorted(notes_in_beat, key=lambda x: x['beat'])

        for note_info in sorted_notes:
            beat_fraction = note_info['beat'] % 1
            drums = note_info['drums']

            # 计算三连音内的偏移
            if abs(beat_fraction - 0.0) < 0.01:  # 第一个三连音
                triplet_offset = 0
            elif abs(beat_fraction - 0.67) < 0.01:  # 第二个三连音
                triplet_offset = 2 / 3
            else:  # 其他位置按比例计算
                triplet_offset = beat_fraction

            note_offset = beat_offset + triplet_offset
            drums_str = '|'.join(drums)

            # 使用更精确的三连音时长
            note_duration = 2 / 3 if abs(beat_fraction - 0.67) < 0.01 else 1 / 3

            self.add_note(drums_str, note_duration, note_offset, note_info['accent'])

    def _generate_regular_pattern(self, pattern, bars):
        """生成普通节奏型（无三连音）"""
        for bar in range(bars):
            bar_offset = bar * self.numerator

            for i, note_info in enumerate(pattern):
                beat_offset = note_info['beat'] - 1  # 转换为0基础偏移
                drums_str = '|'.join(note_info['drums'])

                # 计算音符时长
                note_duration = self._calculate_note_duration_in_pattern(note_info, pattern, i)

                self.add_note(
                    drums_str,
                    note_duration,
                    bar_offset + beat_offset,
                    note_info['accent']
                )

    def _calculate_note_duration_in_pattern(self, current_note, pattern, current_index=None):
        """计算节奏型中音符的时长"""
        if current_index is None:
            # 找到当前音符在pattern中的索引
            current_index = next((i for i, note in enumerate(pattern) if note == current_note), 0)

        if current_index < len(pattern) - 1:
            # 不是最后一个音符，计算到下一个音符的间隔
            next_beat = pattern[current_index + 1]['beat']
            current_beat = current_note['beat']
            return next_beat - current_beat
        else:
            # 是最后一个音符，根据节奏型的密度推断时长
            beat_intervals = []
            for i in range(len(pattern) - 1):
                interval = pattern[i + 1]['beat'] - pattern[i]['beat']
                beat_intervals.append(interval)

            if beat_intervals:
                # 使用最常见的间隔作为最后一个音符的时长
                avg_interval = sum(beat_intervals) / len(beat_intervals)
                return avg_interval
            else:
                return 0.5  # 默认8分音符

    def add_random_snare(self, pattern, probability=0.3):
        """随机添加军鼓音符

        Args:
            pattern: 原始节奏型
            probability: 添加军鼓的概率

        Returns:
            list: 修改后的节奏型
        """
        modified_pattern = copy.deepcopy(pattern)

        for note_info in modified_pattern:
            # 如果当前位置没有军鼓且随机概率满足，则添加军鼓
            if 'snare' not in note_info['drums'] and random.random() < probability:
                note_info['drums'].append('snare')
                # 添加军鼓时通常设为重音
                note_info['accent'] = True

        return modified_pattern

    def add_random_bass(self, pattern, probability=0.2):
        """随机添加底鼓音符

        Args:
            pattern: 原始节奏型
            probability: 添加底鼓的概率

        Returns:
            list: 修改后的节奏型
        """
        modified_pattern = copy.deepcopy(pattern)

        for note_info in modified_pattern:
            # 如果当前位置没有底鼓且随机概率满足，则添加底鼓
            if 'bass' not in note_info['drums'] and random.random() < probability:
                note_info['drums'].append('bass')

        return modified_pattern

    def random_modify_notes(self, pattern, add_probability=0.15, remove_probability=0.1):
        """随机增减音符

        Args:
            pattern: 原始节奏型
            add_probability: 添加音符的概率
            remove_probability: 移除音符的概率

        Returns:
            list: 修改后的节奏型
        """
        modified_pattern = copy.deepcopy(pattern)
        available_drums = ['closed_hihat', 'open_hihat', 'ride', 'crash', 't1', 't2', 't3']

        for note_info in modified_pattern:
            # 随机添加音符
            if random.random() < add_probability:
                # 选择一个不在当前drums列表中的鼓
                possible_adds = [drum for drum in available_drums if drum not in note_info['drums']]
                if possible_adds:
                    new_drum = random.choice(possible_adds)
                    note_info['drums'].append(new_drum)

            # 随机移除音符（但保留至少一个音符）
            if len(note_info['drums']) > 1 and random.random() < remove_probability:
                # 不移除bass和snare，优先移除其他鼓
                removable_drums = [drum for drum in note_info['drums']
                                   if drum not in ['bass', 'snare']]
                if removable_drums:
                    drum_to_remove = random.choice(removable_drums)
                    note_info['drums'].remove(drum_to_remove)
                elif len(note_info['drums']) > 1:
                    # 如果只有bass和snare，随机移除一个
                    drum_to_remove = random.choice(note_info['drums'])
                    note_info['drums'].remove(drum_to_remove)

        return modified_pattern

    def create_pattern_variant(self, pattern, variant_type='random'):
        """创建节奏型变体

        Args:
            pattern: 原始节奏型
            variant_type: 变体类型 ('snare', 'bass', 'random', 'all')

        Returns:
            list: 变体节奏型
        """
        if variant_type == 'snare':
            return self.add_random_snare(pattern)
        elif variant_type == 'bass':
            return self.add_random_bass(pattern)
        elif variant_type == 'random':
            return self.random_modify_notes(pattern)
        elif variant_type == 'all':
            # 应用所有变体
            variant = self.add_random_snare(pattern, 0.2)
            variant = self.add_random_bass(variant, 0.15)
            variant = self.random_modify_notes(variant, 0.1, 0.05)
            return variant
        else:
            return copy.deepcopy(pattern)

    def save_midi(self, filename=None):
        """保存MIDI文件"""
        if filename is None:
            filename = f"random_drum_beat_{self.bpm}bpm_{self.bars}bars.mid"

        # 确保输出目录存在
        output_path = self.run_config.get('output_path', '../music/outputs/')
        os.makedirs(output_path, exist_ok=True)

        # 将鼓声部添加到主音乐流
        self.score.append(self.drum_part)

        # 保存文件
        full_path = os.path.join(output_path, filename)
        self.score.write('midi', fp=full_path)

        print(f"MIDI文件已保存到: {full_path}")
        return full_path

def main():
    """主程序"""
    print("架子鼓节奏型生成器")
    print("=" * 40)

    # 创建生成器实例
    generator = DrumSheetGenerator()

    # 获取所有可用的节奏型
    available_patterns = {
        'standard_rock': RhythmPatterns.standard_rock(),
        'disco_pattern': RhythmPatterns.disco_pattern(),
        'shuffle_pattern': RhythmPatterns.shuffle_pattern(),
        'funk_pattern': RhythmPatterns.funk_pattern(),
        'ballad_pattern': RhythmPatterns.ballad_pattern(),
        'reggae_pattern': RhythmPatterns.reggae_pattern(),
    }

    # 选择一个节奏型（这里选择基本摇滚节奏）
    pattern_name = 'standard_rock'
    original_pattern = available_patterns[pattern_name]

    print(f"\n选择的节奏型: {pattern_name}")
    print(f"原始节奏型包含 {len(original_pattern)} 个音符")

    # 生成原始节奏型MIDI
    print("\n生成原始节奏型...")
    generator.generate_from_pattern(original_pattern, bars=4)
    original_midi_path = generator.save_midi(f"{pattern_name}_original.mid")

    # 生成变体1：添加随机军鼓
    print("\n生成军鼓变体...")
    snare_variant = generator.create_pattern_variant(original_pattern, 'snare')
    generator = DrumSheetGenerator()  # 重新初始化
    generator.generate_from_pattern(snare_variant, bars=4)
    snare_midi_path = generator.save_midi(f"{pattern_name}_snare_variant.mid")

    # 生成变体2：添加随机底鼓
    print("\n生成底鼓变体...")
    bass_variant = generator.create_pattern_variant(original_pattern, 'bass')
    generator = DrumSheetGenerator()  # 重新初始化
    generator.generate_from_pattern(bass_variant, bars=4)
    bass_midi_path = generator.save_midi(f"{pattern_name}_bass_variant.mid")

    # 生成变体3：随机增减音符
    print("\n生成随机变体...")
    random_variant = generator.create_pattern_variant(original_pattern, 'random')
    generator = DrumSheetGenerator()  # 重新初始化
    generator.generate_from_pattern(random_variant, bars=4)
    random_midi_path = generator.save_midi(f"{pattern_name}_random_variant.mid")

    # 生成变体4：综合变体
    print("\n生成综合变体...")
    all_variant = generator.create_pattern_variant(original_pattern, 'all')
    generator = DrumSheetGenerator()  # 重新初始化
    generator.generate_from_pattern(all_variant, bars=4)
    all_midi_path = generator.save_midi(f"{pattern_name}_all_variant.mid")

    # 打印生成结果
    print(f"\n生成完成！")
    print(f"BPM: {generator.bpm}")
    print(f"拍号: {generator.numerator}/{generator.denominator}")
    print(f"小节数: 4")
    print("\n生成的文件:")
    print(f"1. 原始节奏型: {original_midi_path}")
    print(f"2. 军鼓变体: {snare_midi_path}")
    print(f"3. 底鼓变体: {bass_midi_path}")
    print(f"4. 随机变体: {random_midi_path}")
    print(f"5. 综合变体: {all_midi_path}")


if __name__ == "__main__":
    main()
