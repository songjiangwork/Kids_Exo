import { AfterViewInit, Component, EventEmitter, Input, OnChanges, Output, ViewChild } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSelectModule } from '@angular/material/select';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { SessionSummary } from '../core/practice-api';

interface HistoryFilter {
  status: string;
  subject: string;
  search: string;
}

@Component({
  selector: 'app-practice-history-table',
  imports: [
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatPaginatorModule,
    MatSelectModule,
    MatSortModule,
    MatTableModule,
    RouterLink,
  ],
  templateUrl: './practice-history-table.html',
  styleUrl: './practice-history-table.scss',
})
export class PracticeHistoryTable implements AfterViewInit, OnChanges {
  @Input() sessions: SessionSummary[] = [];
  @Output() reviewResults = new EventEmitter<SessionSummary>();

  @ViewChild(MatPaginator) private paginator?: MatPaginator;
  @ViewChild(MatSort) private sort?: MatSort;

  protected readonly displayedColumns = [
    'date',
    'skill',
    'subject',
    'category',
    'status',
    'score',
    'accuracy',
    'time',
    'actions',
  ];
  protected readonly dataSource = new MatTableDataSource<SessionSummary>([]);
  protected readonly statusOptions = ['created', 'in_progress', 'completed'];
  protected filter: HistoryFilter = { status: '', subject: '', search: '' };

  ngOnChanges(): void {
    this.configureDataSource();
  }

  ngAfterViewInit(): void {
    this.configureDataSource();
  }

  protected subjects(): string[] {
    return Array.from(new Set(this.sessions.map((session) => session.subject))).sort();
  }

  protected setStatus(value: string): void {
    this.filter = { ...this.filter, status: value };
    this.applyFilter();
  }

  protected setSubject(value: string): void {
    this.filter = { ...this.filter, subject: value };
    this.applyFilter();
  }

  protected setSearch(value: string): void {
    this.filter = { ...this.filter, search: value.trim().toLowerCase() };
    this.applyFilter();
  }

  protected accuracy(session: SessionSummary): number {
    return session.total_questions ? session.correct_answers / session.total_questions : 0;
  }

  protected formatPercent(ratio: number): string {
    return `${Math.round(ratio * 100)}%`;
  }

  protected formatTime(seconds: number | null): string {
    if (seconds === null) {
      return 'No time';
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  protected formatDate(value?: string | null): string {
    if (!value) {
      return 'No date';
    }
    return new Intl.DateTimeFormat('en-CA', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(new Date(value));
  }

  private configureDataSource(): void {
    this.dataSource.data = [...this.sessions].sort((left, right) => {
      const leftDate = Date.parse(left.created_at ?? left.completed_at ?? '');
      const rightDate = Date.parse(right.created_at ?? right.completed_at ?? '');
      if (Number.isNaN(leftDate) || Number.isNaN(rightDate)) {
        return 0;
      }
      return rightDate - leftDate;
    });
    this.dataSource.filterPredicate = (session, filterValue) => {
      const parsed = JSON.parse(filterValue) as HistoryFilter;
      if (parsed.status && session.status !== parsed.status) {
        return false;
      }
      if (parsed.subject && session.subject !== parsed.subject) {
        return false;
      }
      const haystack = `${session.skill} ${session.plugin} ${session.subject} ${session.category}`.toLowerCase();
      return haystack.includes(parsed.search);
    };
    this.dataSource.sortingDataAccessor = (session, column) => {
      switch (column) {
        case 'date':
          return Date.parse(session.created_at ?? session.completed_at ?? '') || 0;
        case 'score':
        case 'accuracy':
          return this.accuracy(session);
        case 'time':
          return session.elapsed_seconds ?? -1;
        default:
          return String((session as unknown as Record<string, unknown>)[column] ?? '');
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
