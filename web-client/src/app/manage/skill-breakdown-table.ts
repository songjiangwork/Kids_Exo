import { AfterViewInit, Component, Input, OnChanges, ViewChild } from '@angular/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { LearnerSkillBreakdown } from '../core/practice-api';

@Component({
  selector: 'app-skill-breakdown-table',
  imports: [MatFormFieldModule, MatInputModule, MatSortModule, MatTableModule],
  templateUrl: './skill-breakdown-table.html',
  styleUrl: './skill-breakdown-table.scss',
})
export class SkillBreakdownTable implements AfterViewInit, OnChanges {
  @Input() skills: LearnerSkillBreakdown[] = [];

  @ViewChild(MatSort) private sort?: MatSort;

  protected readonly displayedColumns = ['skill', 'correct', 'total', 'accuracy', 'focus'];
  protected readonly dataSource = new MatTableDataSource<LearnerSkillBreakdown>([]);

  ngOnChanges(): void {
    this.configureDataSource();
  }

  ngAfterViewInit(): void {
    this.configureDataSource();
  }

  protected setSearch(value: string): void {
    this.dataSource.filter = value.trim().toLowerCase();
  }

  protected formatPercent(ratio: number): string {
    return `${Math.round(ratio * 100)}%`;
  }

  protected focusLabel(skill: LearnerSkillBreakdown): string {
    if (skill.total_questions === 0) {
      return 'No data';
    }
    if (skill.accuracy < 0.7) {
      return 'Focus';
    }
    if (skill.accuracy < 0.9) {
      return 'Growing';
    }
    return 'Strong';
  }

  private configureDataSource(): void {
    this.dataSource.data = this.skills;
    this.dataSource.filterPredicate = (skill, filterValue) =>
      `${skill.title} ${skill.plugin}`.toLowerCase().includes(filterValue);
    this.dataSource.sortingDataAccessor = (skill, column) => {
      switch (column) {
        case 'skill':
          return skill.title;
        case 'correct':
          return skill.correct_answers;
        case 'total':
          return skill.total_questions;
        case 'accuracy':
          return skill.accuracy;
        default:
          return String((skill as unknown as Record<string, unknown>)[column] ?? '');
      }
    };
    if (this.sort) {
      this.dataSource.sort = this.sort;
    }
  }
}
