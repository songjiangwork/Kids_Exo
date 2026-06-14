import { AfterViewInit, Component, EventEmitter, Input, OnChanges, Output, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSelectModule } from '@angular/material/select';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { LearnerMistakeEntry } from '../core/practice-api';

interface MistakeFilter {
  plugin: string;
  search: string;
  minMissed: number;
}

@Component({
  selector: 'app-mistake-notebook-table',
  imports: [
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatPaginatorModule,
    MatSelectModule,
    MatSortModule,
    MatTableModule,
  ],
  templateUrl: './mistake-notebook-table.html',
  styleUrl: './mistake-notebook-table.scss',
})
export class MistakeNotebookTable implements AfterViewInit, OnChanges {
  @Input() mistakes: LearnerMistakeEntry[] = [];
  @Input() creatingPracticePlugin: string | null = null;
  @Input() allowCreatePractice = true;
  @Output() createPracticeFromPlugin = new EventEmitter<string>();

  @ViewChild(MatPaginator) private paginator?: MatPaginator;
  @ViewChild(MatSort) private sort?: MatSort;

  protected displayedColumns(): string[] {
    const columns = [
      'skill',
      'prompt',
      'expected',
      'last',
      'times',
      'lastSeen',
    ];
    return this.allowCreatePractice ? [...columns, 'actions'] : columns;
  }
  protected readonly dataSource = new MatTableDataSource<LearnerMistakeEntry>([]);
  protected filter: MistakeFilter = { plugin: '', search: '', minMissed: 0 };

  ngOnChanges(): void {
    this.configureDataSource();
  }

  ngAfterViewInit(): void {
    this.configureDataSource();
  }

  protected skills(): LearnerMistakeEntry[] {
    const seen = new Set<string>();
    return this.mistakes.filter((mistake) => {
      if (seen.has(mistake.plugin)) {
        return false;
      }
      seen.add(mistake.plugin);
      return true;
    });
  }

  protected setPlugin(value: string): void {
    this.filter = { ...this.filter, plugin: value };
    this.applyFilter();
  }

  protected setSearch(value: string): void {
    this.filter = { ...this.filter, search: value.trim().toLowerCase() };
    this.applyFilter();
  }

  protected setMinMissed(value: string): void {
    this.filter = { ...this.filter, minMissed: Number(value) || 0 };
    this.applyFilter();
  }

  protected formatDate(value: string): string {
    return new Intl.DateTimeFormat('en-CA', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(new Date(value));
  }

  protected answerText(value: unknown): string {
    if (value === null || value === undefined) {
      return 'No answer';
    }
    return String(value);
  }

  protected isCreating(pluginId: string): boolean {
    return this.creatingPracticePlugin === pluginId;
  }

  private configureDataSource(): void {
    this.dataSource.data = this.mistakes;
    this.dataSource.filterPredicate = (mistake, filterValue) => {
      const parsed = JSON.parse(filterValue) as MistakeFilter;
      if (parsed.plugin && mistake.plugin !== parsed.plugin) {
        return false;
      }
      if (mistake.times_missed < parsed.minMissed) {
        return false;
      }
      const haystack = `${mistake.title} ${mistake.plugin} ${mistake.prompt}`.toLowerCase();
      return haystack.includes(parsed.search);
    };
    this.dataSource.sortingDataAccessor = (mistake, column) => {
      switch (column) {
        case 'skill':
          return mistake.title;
        case 'times':
          return mistake.times_missed;
        case 'lastSeen':
          return Date.parse(mistake.last_seen_at) || 0;
        default:
          return String((mistake as unknown as Record<string, unknown>)[column] ?? '');
      }
    };
    if (this.paginator) {
      this.dataSource.paginator = this.paginator;
    }
    if (this.sort) {
      this.dataSource.sort = this.sort;
    }
    this.applyFilter();
  }

  private applyFilter(): void {
    this.dataSource.filter = JSON.stringify(this.filter);
    this.dataSource.paginator?.firstPage();
  }
}
